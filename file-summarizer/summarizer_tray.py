import os
import sys
import threading
import pyttsx3
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QFileDialog, QApplication
from PyQt5.QtCore import QSize

# Import the updated LangChain components
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class FileSummarizerTray:
    def __init__(self):
        # Initialize Ollama with your preferred model
        self.llm = OllamaLLM(model="llama3")
        
        # Create a prompt template for file summarization
        self.prompt_template = PromptTemplate(
            input_variables=["file_content"],
            template="Please provide a brief summary of the following file content:\n\n{file_content}\n\nSummary:"
        )
        
        # Create a modern LangChain pipeline
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Flag to check if processing is in progress
        self.is_processing = False
        
        # Setup the application
        self.app = QApplication(sys.argv)
        self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Set up the system tray icon and menu"""
        # Create the tray icon
        self.tray_icon = QSystemTrayIcon()
        
        # Create a simple icon programmatically (for macOS compatibility)
        icon_pixmap = QtGui.QPixmap(16, 16)
        icon_pixmap.fill(QtGui.QColor(0, 120, 212))  # Blue color
        self.tray_icon.setIcon(QtGui.QIcon(icon_pixmap))
        
        # Create the menu
        self.tray_menu = QMenu()
        
        # Add menu actions
        self.open_action = QAction("Summarize File...")
        self.open_action.triggered.connect(self.select_file_and_summarize)
        self.tray_menu.addAction(self.open_action)
        
        # Add clipboard action
        self.clipboard_action = QAction("Summarize Clipboard")
        self.clipboard_action.triggered.connect(self.summarize_clipboard)
        self.tray_menu.addAction(self.clipboard_action)
        
        # Add separator
        self.tray_menu.addSeparator()
        
        # Add quit action
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.app.quit)
        self.tray_menu.addAction(self.quit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Show the icon
        self.tray_icon.show()
        
        # Set tooltip
        self.tray_icon.setToolTip("File Summarizer")
        
        # Print console message to confirm tray icon setup
        print("System tray icon set up. If you don't see it, check your menu bar.")
    
    def summarize_file(self, filepath):
        """Summarize the contents of a file"""
        try:
            # Set processing flag
            self.is_processing = True
            
            # Update tray icon to show processing
            self.tray_icon.setToolTip("File Summarizer (Processing...)")
            
            # Read file contents
            with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
                file_content = file.read()
                
            # Truncate if too long (adjust max_length as needed for your model)
            max_length = 4000
            if len(file_content) > max_length:
                file_content = file_content[:max_length] + "...[content truncated]"
                
            # Generate summary
            print(f"Generating summary for {filepath}...")
            result = self.chain.invoke({"file_content": file_content})
            
            # Print the summary
            print(f"Summary of {os.path.basename(filepath)}: {result}")
            
            # Show notification
            self.tray_icon.showMessage(
                f"Summary of {os.path.basename(filepath)}",
                result,
                QSystemTrayIcon.Information,
                10000  # Display for 10 seconds
            )
            
            # Speak the summary
            self.speak(f"Here's the summary of {os.path.basename(filepath)}: {result}")
            
            # Reset processing flag and tooltip
            self.is_processing = False
            self.tray_icon.setToolTip("File Summarizer")
            
            return result
            
        except Exception as e:
            error_msg = f"Error summarizing file: {e}"
            print(error_msg)
            self.tray_icon.showMessage(
                "Error",
                error_msg,
                QSystemTrayIcon.Critical,
                5000
            )
            self.is_processing = False
            self.tray_icon.setToolTip("File Summarizer")
            return None
    
    def summarize_clipboard(self):
        """Summarize text from clipboard"""
        if self.is_processing:
            return
            
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text:
            self.tray_icon.showMessage(
                "Error",
                "Clipboard is empty or doesn't contain text",
                QSystemTrayIcon.Information,
                3000
            )
            return
            
        # Process in a separate thread
        self.is_processing = True
        threading.Thread(target=self._process_clipboard_text, args=(text,)).start()
    
    def _process_clipboard_text(self, text):
        try:
            # Truncate if too long
            max_length = 4000
            if len(text) > max_length:
                text = text[:max_length] + "...[content truncated]"
                
            # Generate summary
            print("Generating summary for clipboard content...")
            result = self.chain.invoke({"file_content": text})
            
            # Show notification
            self.tray_icon.showMessage(
                "Clipboard Summary",
                result,
                QSystemTrayIcon.Information,
                10000
            )
            
            # Speak the summary
            self.speak(f"Here's the summary of the clipboard content: {result}")
        except Exception as e:
            error_msg = f"Error summarizing clipboard: {e}"
            print(error_msg)
            self.tray_icon.showMessage(
                "Error",
                error_msg,
                QSystemTrayIcon.Critical,
                5000
            )
        finally:
            self.is_processing = False
    
    def speak(self, text):
        """Convert text to speech"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def select_file_and_summarize(self):
        """Open file dialog and summarize selected file"""
        if self.is_processing:
            self.tray_icon.showMessage(
                "Processing in Progress",
                "Already processing a file, please wait...",
                QSystemTrayIcon.Information,
                3000
            )
            return
            
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                None,
                "Select file to summarize",
                "",
                "All Files (*);;Text Files (*.txt);;Python Files (*.py);;Markdown Files (*.md)"
            )
            
            if filepath:
                # Summarize in a separate thread to keep UI responsive
                threading.Thread(target=self.summarize_file, args=(filepath,)).start()
            
        except Exception as e:
            print(f"Error selecting file: {e}")
    
    def run(self):
        """Run the application"""
        print("File Summarizer running in system tray")
        print("Look for the blue square icon in your menu bar")
        print("Right-click the tray icon to summarize a file or quit")
        return self.app.exec_()

if __name__ == "__main__":
    tray_app = FileSummarizerTray()
    sys.exit(tray_app.run())