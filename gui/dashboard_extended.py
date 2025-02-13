import customtkinter as ctk
from PIL import Image, ImageTk
from utils.file_handler import append_to_file, remove_line_from_file

from proxy.proxy_server import start_proxy 
from malware_detector.file_processor import start_file_processor

ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue") 

button_color = "#07c8ff"

list_color = '#052e5b'

bg_clr = "#001e43"

bold_font = ("Arial", 12, "bold") 


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WebShield")
        self.geometry("640x360")

        self.background_image = Image.open("assets/bg.jpg") 
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        self.welcome_tab = self.tabview.add("Home")
        self.blocked_domains_tab = self.tabview.add("Blocked Domains")
        self.downloaded_files_tab = self.tabview.add("Downloaded Files")
        self.deleted_files_tab = self.tabview.add("Deleted Files")  
        self.block_website_tab = self.tabview.add("Block a Website")  
        self.add_exception_tab = self.tabview.add("Add an Exception")  
        
        self.setup_tab(self.welcome_tab)
        self.setup_welcome_tab()
        
        self.setup_tab(self.blocked_domains_tab)
        self.setup_blocked_domains_tab()
        
        self.setup_tab(self.downloaded_files_tab)
        self.setup_downloaded_files_tab()
        
        self.setup_tab(self.deleted_files_tab)
        self.setup_deleted_files_tab()
        
        self.setup_tab(self.block_website_tab)
        self.setup_block_website_tab()
        
        self.setup_tab(self.add_exception_tab)
        self.setup_add_exception_tab()

    def setup_tab(self, tab):
        background_label = ctk.CTkLabel(tab, text="Setup", image=self.background_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def setup_welcome_tab(self):
        self.welcome_image_original = Image.open("assets/bg.jpg") 
        self.welcome_photo = ImageTk.PhotoImage(self.welcome_image_original)

        self.welcome_label = ctk.CTkLabel(self.welcome_tab, text="A lightweight web shield that safeguards your browsing\n from malicious sites and malware files online!", image=self.welcome_photo)
        self.welcome_label.place(relx=0.5, rely=0.5, anchor="center") 

        self.welcome_label = ctk.CTkLabel(self.welcome_tab, text="A lightweight web shield that safeguards your browsing\n from malicious sites and malware files online!", image=self.welcome_photo)
        self.welcome_label.place(relx=0.5, rely=0.6, anchor="center")        

        self.start_button = ctk.CTkButton(self.welcome_tab, text="Start WebShield", bg_color=bg_clr, command=self.start_webshield, fg_color=button_color)
        self.start_button.place(relx=0.36, rely=0.4, anchor="center")

        self.stop_button = ctk.CTkButton(self.welcome_tab, text="Stop WebShield", bg_color=bg_clr, command=self.stop_webshield, fg_color="#c82929", hover_color="#8a0f0f")
        self.stop_button.place(relx=0.64, rely=0.4, anchor="center")

    def setup_blocked_domains_tab(self):
        # Check if the scrollable frame already exists
        if hasattr(self, 'scrollable_frame'):
            # Destroy old widgets inside the frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        else:
            self.scrollable_frame = ctk.CTkScrollableFrame(self.blocked_domains_tab)
            self.scrollable_frame.pack(expand=True, fill="both")

        blocked_domains = self.load_blocked_domains()

        for i, domain in enumerate(reversed(blocked_domains)):
            textbox = ctk.CTkTextbox(
                self.scrollable_frame, 
                width=600, 
                height=1,  
                font=bold_font, 
                fg_color=list_color
            )
            textbox.grid(row=i, column=0, padx=1, pady=1) 
            textbox.insert("0.0", domain)
            textbox.configure(state="disabled") 

    def setup_downloaded_files_tab(self):
        # Check if the scrollable frame already exists
        if hasattr(self, 'scrollable_frame2'):
            # Destroy old widgets inside the frame
            for widget in self.scrollable_frame2.winfo_children():
                widget.destroy()
        else:
            # Create the scrollable frame if it doesn't exist
            self.scrollable_frame2 = ctk.CTkScrollableFrame(self.downloaded_files_tab)
            self.scrollable_frame2.pack(expand=True, fill="both")

        downloaded_files = self.load_downloaded_files()

        for i, file in enumerate(reversed(downloaded_files)):
            textbox = ctk.CTkTextbox(
                self.scrollable_frame2, 
                width=600,   
                height=1,    
                font=bold_font, 
                fg_color=list_color 
            )
            textbox.grid(row=i, column=0, padx=1, pady=1)  
            textbox.insert("0.0", file)
            textbox.configure(state="disabled")  


    def setup_deleted_files_tab(self):
        # Check if the scrollable frame already exists
        if hasattr(self, 'scrollable_frame3'):
            # Destroy old widgets inside the frame
            for widget in self.scrollable_frame3.winfo_children():
                widget.destroy()
        else:
            self.scrollable_frame3 = ctk.CTkScrollableFrame(self.deleted_files_tab)
            self.scrollable_frame3.pack(expand=True, fill="both")

        deleted_files = self.load_deleted_files()

        for i, file in enumerate(reversed(deleted_files)):
            textbox = ctk.CTkTextbox(
                self.scrollable_frame3,
                width=600,
                height=1,   
                font=bold_font, 
                fg_color=list_color
            )
            textbox.grid(row=i, column=0, padx=1, pady=1) 
            textbox.insert("0.0", file)
            textbox.configure(state="disabled") 

    def setup_block_website_tab(self):

        self.welcome_image_original = Image.open("assets/bg2.jpg") 
        self.welcome_photo2 = ImageTk.PhotoImage(self.welcome_image_original)

        self.welcome_image_original = Image.open("assets/transparent.png") 
        self.welcome_photo3 = ImageTk.PhotoImage(self.welcome_image_original)

        self.welcome_label = ctk.CTkLabel(self.block_website_tab, text="", image=self.welcome_photo2)
        self.welcome_label.place(relx=0.5, rely=0.5, anchor="center")

        self.welcome_label = ctk.CTkLabel(self.block_website_tab, text="Enter a website/url to block it!", bg_color="#001343")
        self.welcome_label.place(relx=0.5, rely=0.25, anchor="center")

        self.website_input = ctk.CTkEntry(
            self.block_website_tab,
            width=400,
            bg_color=bg_clr
        )
        self.website_input.place(relx=0.5, rely=0.45, anchor="center")

        self.block_button = ctk.CTkButton(self.block_website_tab, text="Block Website", bg_color=bg_clr, command=self.block_website, fg_color=button_color)
        self.block_button.place(relx=0.5, rely=0.69, anchor="center")

    def setup_add_exception_tab(self):

        self.welcome_image_original = Image.open("assets/bg2.jpg") 
        self.welcome_photo2 = ImageTk.PhotoImage(self.welcome_image_original)

        self.welcome_image_original = Image.open("assets/transparent.png") 
        self.welcome_photo3 = ImageTk.PhotoImage(self.welcome_image_original)

        self.welcome_label = ctk.CTkLabel(self.add_exception_tab, text="", image=self.welcome_photo2)
        self.welcome_label.place(relx=0.5, rely=0.5, anchor="center")

        self.welcome_label = ctk.CTkLabel(self.add_exception_tab, text="Enter a website/url to unblock it!", bg_color="#001343")
        self.welcome_label.place(relx=0.5, rely=0.25, anchor="center")

        self.exception_input = ctk.CTkEntry(
            self.add_exception_tab, 
            width=400,
            bg_color=bg_clr
        )
        self.exception_input.place(relx=0.5, rely=0.45, anchor="center")

        self.exception_button = ctk.CTkButton(self.add_exception_tab, text="Add Exception", bg_color=bg_clr, command=self.add_exception, fg_color=button_color)
        self.exception_button.place(relx=0.5, rely=0.69, anchor="center")

    def load_blocked_domains(self):
        try:
            with open("history/blocked_domains.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return ["No blocked domains found."]

    def load_downloaded_files(self):
        try:
            with open("history/downloaded_files.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return ["No downloaded files found."]

    def load_deleted_files(self):
        try:
            with open("history/deleted_files.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return ["No deleted files found."]

    def block_website(self):
        website = self.website_input.get()
        if not website:
            print("Please enter a website to block.")
            return
        append_to_file("manual_data/blacklist.txt", website)
        remove_line_from_file("manual_data/whitelist.txt", website)
        print(f"Website to block: {website}")
        self.website_input.delete(0, 'end')
        self.setup_blocked_domains_tab()

    def add_exception(self):
        exception = self.exception_input.get()
        if not exception:
            print("Please enter a website to block.")
            return
        append_to_file("manual_data/whitelist.txt", exception)
        remove_line_from_file("manual_data/blacklist.txt", exception)
        print(f"Exception to add: {exception}")
        self.exception_input.delete(0, 'end')

    

    def run_proxy(self):
        start_proxy(self)

    def run_file_processor(self):
        start_file_processor(self)

    

    def start_webshield(self):
        import threading
        if not hasattr(self, 'proxy_thread') or not self.proxy_thread.is_alive():
            self.proxy_thread = threading.Thread(target=self.run_proxy, daemon=True)
            self.proxy_thread.start()
            print("Proxy Server started!")
        else:
            print("Proxy Server is already running.")

        if not hasattr(self, 'file_processor_thread') or not self.file_processor_thread.is_alive():
            self.file_processor_thread = threading.Thread(target=self.run_file_processor, daemon=True)
            self.file_processor_thread.start()
            print("File Monitor started!")
        else:
            print("File Monitor is already running.")


    def stop_webshield(self):
        print("WebShield stopped!")

    def run(self):
        self.mainloop()     
    

# if __name__ == "__main__":
#     app = Dashboard()
#     app.run()
