import customtkinter
from pytubefix import YouTube as YT
import threading
import os
from moviepy.editor import VideoFileClip, AudioFileClip

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
        self.geometry("850x520")
        self.minsize(720,520)
        self.maxsize(850,750)
        self.title("PYTDL")
        #self.iconbitmap("PYTDL.ico")
        
        #Some constants and variables
        self.TITLE_FONT = customtkinter.CTkFont(family="Arial", size=20, weight="bold")
        self.SUBTITLE_FONT = customtkinter.CTkFont(family="Arial", size=16, weight="normal")
        self.DEFAULT_DOWNLOAD_DIR = "C:\\Users\\username\\Downloads"
        self.DEFAULT_DOWNLOAD_DIR = self.DEFAULT_DOWNLOAD_DIR.replace("username", os.getlogin())
        print("The default download directory is: ", self.DEFAULT_DOWNLOAD_DIR)
        self.download_dir = self.DEFAULT_DOWNLOAD_DIR
      
        #Add UI elements (Widgets)
        
        #Add Title
        self.title = customtkinter.CTkLabel(self, text="Python YouTube DownLoader", font=self.TITLE_FONT)
        self.title.pack(padx=10, pady=10)
        

        #Add Input fields
        #Input field 1
        #Add Subtitle
        self.subtitle = customtkinter.CTkLabel(self, text="Insert a Youtube link:", font=self.SUBTITLE_FONT)
        self.subtitle.pack(pady=20)
        #Add Url text field
        self.url_var = customtkinter.StringVar()
        self.link_field = customtkinter.CTkEntry(self, width=400, height=40, textvariable=self.url_var, font=self.SUBTITLE_FONT, placeholder_text="Enter a YouTube link here", placeholder_text_color="white")
        self.link_field.pack(pady=10)
        #Input field 2
        #Add Subtitle 2
        self.subtitle = customtkinter.CTkLabel(self, text="Insert directory:", font=self.SUBTITLE_FONT)
        self.subtitle.pack(pady=20)
        #Add Download field
        self.dir_var = customtkinter.StringVar()
        self.dir_field = customtkinter.CTkEntry(self, width=400, height=40, textvariable=self.dir_var, font=self.SUBTITLE_FONT, placeholder_text="Enter a directory to save the file", placeholder_text_color="white")
        self.dir_field.pack(pady=10)
        self.dir_var.set(self.DEFAULT_DOWNLOAD_DIR)
        
        #Progress bar and percentage
        #Add progress bar
        self.percentage_var = customtkinter.StringVar()
        self.progress_bar = customtkinter.CTkProgressBar(self, width=400, height=20, corner_radius=8, border_width=0, progress_color="gray", bg_color="gray14")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        #Add progress percentage text
        self.progress_label = customtkinter.CTkLabel(self, text="0%", font=self.SUBTITLE_FONT)
        self.progress_label.pack(pady=2)

        #Add buttons
        #Add Download Video Button
        self.download_video_button = customtkinter.CTkButton(self, width=140, height=30, corner_radius=8, border_width=1, text="Download as video", command=lambda: threading.Thread(target=self.start_video_download).start())
        self.download_video_button.pack(pady=2)
        #Add Download Audio Button
        self.download_audio_button = customtkinter.CTkButton(self, width=140, height=30, corner_radius=8, border_width=1, text="Download as audio", command=lambda: threading.Thread(target=self.start_audio_download).start())
        self.download_audio_button.pack(pady=2)

        #Add error feedback text (we make it invisible so it can be later changed)
        self.status_label = customtkinter.CTkLabel(self, text_color="gray14", text="", font=self.SUBTITLE_FONT)
        self.status_label.pack()
        
    def start_video_download(self):
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        try:
            print("The link is: ", self.url_var.get())
            dir_path = self.dir_var.get()
            if os.path.isdir(dir_path) and dir_path.strip():
                self.download_dir = dir_path
                self.status_label.configure(text="Download directory set successfully!", text_color="green")
            else:
                self.status_label.configure(text="Invalid directory. Using default download directory instead.", text_color="yellow")
                self.download_dir = self.DEFAULT_DOWNLOAD_DIR
            print("The dir is: ", self.download_dir)
            
            YT_link = self.url_var.get()
            YT_object = YT(YT_link, on_progress_callback=self.on_progress)
            video_stream = YT_object.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
            audio_stream = YT_object.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
            
            #Download the video and audio files
            try:
                self.status_label.configure(text="Downloading Video...", text_color="yellow")
                video_stream.download(output_path=self.download_dir,filename='video.mp4')
            except Exception as e:
                self.status_label.configure(text=f"An error occurred while downloading the video.\nError: {e}", text_color="red")
                breakpoint()
            try:
                self.status_label.configure(text="Downloading Audio...", text_color="yellow")
                audio_stream.download(output_path=self.download_dir,filename='audio.mp4')
            except Exception as e:
                self.status_label.configure(text=f"An error occurred while downloading the audio.\nError: {e}", text_color="red")
                breakpoint()  
            
            #Make the video and audio clips
            try:
                self.status_label.configure(text="Combining video...", text_color="yellow")
                video_clip = VideoFileClip(os.path.join(self.download_dir, 'video.mp4'))
            except Exception as e:
                self.status_label.configure(text=f"An error occurred while making the video clip.\nError: {e}", text_color="red")
                breakpoint()
            try:
                self.status_label.configure(text="Combining audio...", text_color="yellow")
                audio_clip = AudioFileClip(os.path.join(self.download_dir, 'audio.mp4'))
            except Exception as e:
                self.status_label.configure(text=f"An error occurred while making the audio clip.\nError: {e}", text_color="red")
                breakpoint()
            
            #Combine the video and audio
            try:
                self.status_label.configure(text="Combining video with audio...", text_color="yellow")
                final_clip = video_clip.set_audio(audio_clip)
            except Exception as e:
                self.status_label.configure(text=f"An error occurred while combining the video with audio.\nError: {e}", text_color="red")
                breakpoint()

            try:
                self.status_label.configure(text="Writing final video...", text_color="yellow")
                final_clip.write_videofile(os.path.join(self.download_dir, f"{YT_object.title}.mp4"))
            except Exception as e:
                self.status_label.configure(text=f"An error occurred while writing the final video.\nError: {e}", text_color="red")
                breakpoint()
            
            #Delete the video and audio files
            #Non metto la try/except perchè se non vanno a buon fine non mi interessa
            os.remove(os.path.join(self.download_dir, 'video.mp4'))
            os.remove(os.path.join(self.download_dir, 'audio.mp4'))
            
            self.status_label.configure(text="Download completed!", text_color="green")
        except Exception as e:
            self.status_label.configure(text_color="red", text=f"An error occurred: {e}")
            print(f"An error occurred: {e}")
        
    def start_audio_download(self):
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        try:
            print("The link is: ", self.url_var.get())
            dir_path = self.dir_var.get()
            if os.path.isdir(dir_path) and dir_path.strip():
                self.download_dir = dir_path
                self.status_label.configure(text="Download directory set successfully!", text_color="green")
            else:
                self.status_label.configure(text="Invalid directory. Using default download directory instead.", text_color="yellow")
                self.download_dir = self.DEFAULT_DOWNLOAD_DIR
            print("The dir is: ", self.download_dir)
            
            YT_link = self.url_var.get()
            YT_object = YT(YT_link, on_progress_callback=self.on_progress)
            audio_stream = YT_object.streams.filter(only_audio=True).first()
            self.status_label.configure(text=f"Downloading:\n{YT_object.title}\nIn:{self.download_dir}", text_color="yellow")
            audio_file = audio_stream.download(output_path=self.download_dir)
            
            # Convert to mp3
            base, ext = os.path.splitext(audio_file)
            new_file = base + '.mp3'
            os.rename(audio_file, new_file)
            
            self.status_label.configure(text="Download completed!", text_color="green")
        except Exception as e:
            self.status_label.configure(text_color="red", text=f"An error occurred: {e}")
            print(f"An error occurred: {e}")

    #Progress callback function
    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_bar.set(percentage/100)
        self.progress_label.configure(text=f"{percentage:.2f}%")

#Run app
YTDLInstance = YTDLApp()
YTDLInstance.mainloop() 