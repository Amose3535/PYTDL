import tkinter
import customtkinter
from pytube import YouTube as YT
import time

#System settings.
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

#App class
class YTDLApp(customtkinter.CTk):    
    #Initialization function (called when making a new instance of YTDLApp)
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        #print(self.cget("bg")) <<< Used to know that the bgcolor is gray14
        
        #App windows settings
        self.geometry("720x480")
        self.minsize(720,480)
        self.maxsize(850,750)
        self.title("PYTDL")
        
        #Some constants
        self.TITLE_FONT = customtkinter.CTkFont(family="Arial", size=20, weight="bold")
        self.SUBTITLE_FONT = customtkinter.CTkFont(family="Arial", size=16, weight="normal")
        
        #Bind events to functions
        #self.bind("<EventWhatnot>",self.on_function_name)# <<< Leaving comment to remember about events
        
        #Add UI elements (Widgets)
        
        #Add Title
        self.title = customtkinter.CTkLabel(self, text="Python YouTube DownLoader", font=self.TITLE_FONT)
        self.title.pack(padx=10, pady=10)
        
        #Add Subtitle
        self.subtitle = customtkinter.CTkLabel(self, text="Insert a Youtube link:", font=self.SUBTITLE_FONT)
        self.subtitle.pack(pady=20)
        
        #Add Url text field
        self.url_var = tkinter.StringVar()
        self.link_field = customtkinter.CTkEntry(self, width=400, height=40, textvariable=self.url_var, font=self.SUBTITLE_FONT, placeholder_text="Enter a YouTube link here", placeholder_text_color="white")
        self.link_field.pack(pady=10)
        
        #Add Download Video Button
        self.download_video_button = customtkinter.CTkButton(self, width=140, height=30, corner_radius=8, border_width=1, text="Download as video", command=self.start_video_download)
        self.download_video_button.pack(pady=5)

        #Add Download Audio Button
        self.download_audio_button = customtkinter.CTkButton(self, width=140, height=30, corner_radius=8, border_width=1, text="Download as audio", command=self.start_audio_download)
        self.download_audio_button.pack(pady=5)
        
        #Add error feedback text (we make it invisible so it can be later changed)
        self.error_text = customtkinter.CTkLabel(self, text_color="gray14", text="YouTube link is invalid", font=self.SUBTITLE_FONT)
        self.error_text.pack()
        
    def start_video_download(self):
        try:
            YT_link = self.link_field.get()
            YT_object = YT(YT_link)
            video = YT_object.streams.get_highest_resolution()
            video.download
        except:
            self.error_text.configure(text_color="red")
    
    def start_audio_download(self):
        try:
            pass
        except:
            pass
        
        
        
        
    
        

#Run app
YTDLInstance = YTDLApp()
YTDLInstance.mainloop()






