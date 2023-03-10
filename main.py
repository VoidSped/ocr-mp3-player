import tkinter as tk
from tkinter import ttk
from tkinter import *
import vlc
from time import sleep
from queue_system import queue
from threading import Thread
import youtube_to_mp3
import playlist_management
import settings


class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.geometry('360x640')
        self.resizable(False, False)
        self.title("OCR MP3 Player")
        self.configure(bg=settings.colours["primary"])
        self.dragging = False
        self.music_queue = queue()

        style = ttk.Style(self)
        style.theme_create("dummy", parent="alt", settings={
            "TNotebook": {"configure": {"margins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 1], "background": settings.colours["secondary"]},
                "map": {"background": [("selected", settings.colours["secondary"])],
                        "expand": [("selected", [1, 1, 1, 0])]}}})

        style.theme_use('dummy')
        style.configure('TNotebook.Tab', background=settings.colours["primary"], foreground='white')
        style.map("TNotebook", background=[("selected", settings.colours["secondary"])])

        tabControl = ttk.Notebook(self)
        self.tab1 = Frame(tabControl, background=settings.colours["primary"])
        self.tab2 = Frame(tabControl, background=settings.colours["primary"])
        self.tab3 = Frame(tabControl, background=settings.colours["primary"])
        tabControl.add(self.tab1, text='YouTube MP3 Player')
        tabControl.add(self.tab2, text='My Playlists')
        tabControl.add(self.tab3, text='Settings')
        tabControl.pack(expand=True, fill=BOTH)

        # Tab 1 - YouTube MP3 Downloader

        youtubeMp3DownloaderEntry = tk.Entry(self.tab1, width=30)
        youtubeMp3DownloaderEntry.place(x=90, y=35)

        def download_button_function():
            data = youtubeMp3DownloaderEntry.get()
            title = youtube_to_mp3.get_title(data)
            if title is not None:
                global temporary_label
                temporary_label = tk.Label(self.tab1, text=youtube_to_mp3.get_title(data), font=("Comic Sans", 10))
                temporary_label.place(x=0, y=100)
                global temporary_button
                temporary_button = tk.Button(self.tab1, text="Confirm", font=("Comic Sans", 8),
                                             background=settings.colours["secondary"], command=confirm_button)
                temporary_button.place(x=10, y=130)

        def confirm():
            data = youtubeMp3DownloaderEntry.get()
            progress_label = tk.Label(self.tab1, text='Downloading', fg='black', bg=settings.colours["primary"])
            progress_label.place(x=0, y=160)
            youtube_to_mp3.download_youtube_mp3(data)
            progress_label.configure(text='Success!', fg='light green')
            temporary_label.destroy()
            temporary_button.destroy()

            cleanup(progress_label)

        def confirm_button():

            thread = Thread(target=confirm)
            thread.start()

        def cleanup(label):

            sleep(5)
            label.destroy()

        youtube_label = tk.Label(self.tab1, text="Youtube MP3 Downloader", font=("Comic Sans", 13),
                                 background=settings.colours["secondary"])
        youtube_label.place(x=80, y=10)
        youtube_button = tk.Button(self.tab1, text="Download Now", font=("Comic Sans", 8),
                                   background=settings.colours["secondary"], command=download_button_function)
        youtube_button.place(x=140, y=60)

        # Tab 2 - Playlist System

        scrollbar = tk.Scrollbar(self.tab2, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        text = tk.Text(self.tab2, yscrollcommand=scrollbar.set, height=0, width=0)
        text.place(x=0, y=0)

        def input_playlist_name():
            # Create a new Tkinter window for the user to input a name
            global input_window
            input_window = tk.Tk()
            input_window.title("Input Playlist Name")
            input_window.geometry("200x100")

            # Create a Tkinter Entry widget
            entry = tk.Entry(input_window)
            entry.pack()

            # Create a Tkinter Button widget to submit the name
            submit_button = tk.Button(input_window, text='Submit', command=lambda: submit(entry.get()))
            submit_button.pack()

            # Run the Tkinter event loop for the input window
            input_window.mainloop()

        def submit(name):
            # Close the input window
            if playlist_management.create_playlist(name):
                input_window.destroy()

                # Create a directory based on the input name
                button = tk.Button(self.tab2, text=name, bg=settings.colours["secondary"], width=60,
                                   command=lambda p=name: display_content(p, button))
                button.pack()

        def delete_downloaded_file(listbox):
            selected = listbox.curselection()
            if selected:
                file = listbox.get(selected[0])
                if playlist_management.remove_audio_file_from_downloaded(file):
                    listbox.delete(selected[0])

        def delete_playlist(playlist_arg, p_button, win):

            if playlist_management.delete_playlist(playlist_arg):
                win.destroy()

                p_button.pack_forget()

                for widget in p_button.winfo_children():
                    widget.pack()

                p_button.destroy()

        scrollbar.config(command=text.yview)

        def delete_selected_file(listbox, playlist_arg):
            selected = listbox.curselection()
            if selected:
                file = listbox.get(selected[0])
                if playlist_management.remove_audio_file_from_playlist(file, playlist_arg):
                    listbox.delete(selected[0])

        def get_selected_file(listbox):
            selected = listbox.curselection()
            if selected:
                file = listbox.get(selected[0])
                return file

        def get_playlist(listbox):
            selected = listbox.curselection()
            if selected:
                file = listbox.get(selected[0])
                return file

        def display_downloads():
            playlist_window = tk.Tk()
            playlist_window.title(playlist)
            playlist_window.geometry("200x450")

            scrollbar_for_gui = tk.Scrollbar(playlist_window)
            scrollbar_for_gui.pack(side='right', fill='y')

            listbox = tk.Listbox(playlist_window, yscrollcommand=scrollbar_for_gui.set)
            listbox.pack(fill=BOTH)

            files = playlist_management.display_downloaded_audio()

            for file in files:
                listbox.insert('end', file)

            button = tk.Button(playlist_window, text='Delete Audio', command=lambda: delete_downloaded_file(listbox))
            button.pack()

            move_audio_button = tk.Button(playlist_window, text='Move Audio To..',
                                          command=lambda: move_downloaded_audio_gui(get_selected_file(listbox),
                                                                                    listbox))
            move_audio_button.pack()

            scrollbar_for_gui.configure(command=listbox.yview)
            playlist_window.mainloop()

        def move_audio(file, original_playlist, new_playlist, gui, listbox):

            playlist_management.move_audio_file_from_playlist(file, original_playlist, new_playlist)
            gui.destroy()

            index = listbox.get(0, tk.END).index(file)
            listbox.delete(index)

        def move_downloaded_audio(file, new_playlist, gui, listbox):

            playlist_management.move_audio_file_from_downloaded_audio(file, new_playlist)
            gui.destroy()

            index = listbox.get(0, tk.END).index(file)
            listbox.delete(index)

        def move_downloaded_audio_gui(f, original_listbox):
            playlist_display = tk.Tk()
            playlist_display.title("Playlists")
            playlist_display.geometry("300x500")
            scrollbar_for_gui = tk.Scrollbar(playlist_display)
            scrollbar_for_gui.pack(side='right', fill='y')

            listbox = tk.Listbox(playlist_display, yscrollcommand=scrollbar_for_gui.set)
            listbox.pack(fill=BOTH)

            files = playlist_management.display_playlists()

            for file in files:
                listbox.insert('end', file)

            button = tk.Button(playlist_display, text='Move Audio',
                               command=lambda: move_downloaded_audio(
                                   f,
                                   get_playlist(listbox),
                                   playlist_display, original_listbox))
            button.pack()

            scrollbar_for_gui.configure(command=listbox.yview)
            playlist_display.mainloop()

        def move_audio_gui(f, original_playlist, original_listbox):
            playlist_display = tk.Tk()
            playlist_display.title("Playlists")
            playlist_display.geometry("300x500")
            scrollbar_for_gui = tk.Scrollbar(playlist_display)
            scrollbar_for_gui.pack(side='right', fill='y')

            listbox = tk.Listbox(playlist_display, yscrollcommand=scrollbar_for_gui.set)
            listbox.pack(fill=BOTH)

            files = playlist_management.display_playlists()

            for file in files:
                listbox.insert('end', file)

            button = tk.Button(playlist_display, text='Move Audio',
                               command=lambda: move_audio(f, original_playlist, get_playlist(listbox), playlist_display,
                                                          original_listbox))
            button.pack()

            scrollbar_for_gui.configure(command=listbox.yview)
            playlist_display.mainloop()

        createNewPlaylistButton = tk.Button(self.tab2, text="Create New Playlist", font=("Comic Sans", 15),
                                            background=settings.colours["secondary"], width=33,
                                            command=input_playlist_name)
        createNewPlaylistButton.pack()

        downloadedAudioButton = tk.Button(self.tab2, text="Downloaded Audio", font=("Comic Sans", 15),
                                          background=settings.colours["secondary"], width=33, command=display_downloads)
        downloadedAudioButton.pack()

        for playlist in playlist_management.display_playlists():
            playlist_button = tk.Button(self.tab2, text=playlist, bg=settings.colours["secondary"], width=60,
                                        command=lambda p=playlist: display_content(p, playlist_button))
            playlist_button.pack()

        def on_play_playlist(playlist_to_display, win):

            win.destroy()
            self.player.pause()
            self.music_queue.set_playlist_to_queue(playlist_to_display)
            thread = Thread(target=self.play, args=(self.music_queue.display_queue()[self.music_queue.index],))
            thread.start()

        def display_content(playlist_arg, b):
            playlist_window = tk.Tk()
            playlist_window.title(playlist_arg)
            playlist_window.geometry("200x450")

            scrollbar_for_gui = tk.Scrollbar(playlist_window)
            scrollbar_for_gui.pack(side='right', fill='y')

            listbox = tk.Listbox(playlist_window, yscrollcommand=scrollbar_for_gui.set)
            listbox.pack(fill=BOTH)

            files = playlist_management.display_audio_in_playlist(playlist_arg)

            for file in files:
                listbox.insert('end', file)

            delete_audio_button = tk.Button(playlist_window, text='Delete Audio',
                                            command=lambda: delete_selected_file(listbox, playlist_arg))
            delete_audio_button.pack()

            delete_playlist_button = tk.Button(playlist_window, text='Delete Playlist',
                                               command=lambda: delete_playlist(playlist_arg, b, playlist_window))
            delete_playlist_button.pack()

            move_audio_button = tk.Button(playlist_window, text='Move Audio To..',
                                          command=lambda: move_audio_gui(get_selected_file(listbox), playlist_arg,
                                                                         listbox))
            move_audio_button.pack()

            play_playlist_button = tk.Button(playlist_window, text='Play Playlist',
                                             command=lambda: on_play_playlist(playlist_arg, playlist_window))
            play_playlist_button.pack()

            scrollbar_for_gui.configure(command=listbox.yview)
            playlist_window.mainloop()

        # MP3 Player

        self.player = vlc.MediaPlayer()

        self.buttonFrame = Frame(self.tab2, background=settings.colours['primary'])
        self.buttonFrame.pack(side="bottom", fill="none", pady=10)

        self.progress_bar = tk.Scale(self.tab2, from_=0, to=100, orient="horizontal", sliderlength=20, length=200,
                                     bg= settings.colours["primary"], troughcolor= settings.colours["secondary"], highlightthickness=0, command=self.on_scale_drag)
        self.progress_bar.pack(side="bottom", fill="x")
        self.progress_bar.bind("<ButtonPress-1>", self.on_scale_drag_start)
        self.progress_bar.bind("<B1-Motion>", self.on_scale_drag)
        self.progress_bar.bind("<ButtonRelease-1>", self.on_scale_drag_end)

        self.volume_frame = Frame(self.tab2, background=settings.colours["primary"])
        self.volume_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

        self.volume_label = tk.Label(self.volume_frame, text='Volume', background=settings.colours["secondary"])
        self.volume_label.pack(side=tk.TOP)

        self.volume_slider = tk.Scale(self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                      bg= settings.colours["primary"], troughcolor= settings.colours["secondary"],
                                      highlightthickness=0, command=self.set_volume)
        self.volume_slider.set(100)
        self.volume_slider.pack(side=tk.BOTTOM)

        self.song_name = tk.StringVar()
        self.song_label = tk.Label(self.volume_frame, bg= settings.colours["primary"], textvariable=self.song_name)
        self.song_label.pack(side=tk.BOTTOM)

        self.play_button = tk.Button(self.buttonFrame, text='Play', background = settings.colours['secondary'], command=lambda: self.play(0))
        self.pause_button = tk.Button(self.buttonFrame, text='Pause', background = settings.colours['secondary'], command=self.pause)
        self.backward_button = tk.Button(self.buttonFrame, text='<<', background = settings.colours['secondary'], command=self.backward)
        self.forward_button = tk.Button(self.buttonFrame, text='>>', background = settings.colours['secondary'], command=self.forward)
        self.next_track_button = tk.Button(self.buttonFrame, text='>|', background = settings.colours['secondary'], command=self.skip_forward)
        self.last_track_button = tk.Button(self.buttonFrame, text='|<', background = settings.colours['secondary'], command = self.skip_backward)

        self.last_track_button.pack(side='left', padx=5)
        self.backward_button.pack(side='left', padx=5)
        self.play_button.pack(side='left', padx=5)
        self.pause_button.pack(side='left', padx=5)
        self.forward_button.pack(side='left', padx=5)
        self.next_track_button.pack(side='left', padx=5)




        # Tab 3 - Settings System

        primaryEntry = tk.Entry(self.tab3, width=15)
        primaryEntry.place(x=130, y=60)

        secondaryEntry = tk.Entry(self.tab3, width=15)
        secondaryEntry.place(x=130, y=90)

        def change_primary_colour():
            data = primaryEntry.get().replace(' ', '')
            settings.change_primary(data)
            if settings.is_colour_valid(data):
                style.configure('TNotebook.Tab', background=settings.colours["primary"])

                self.tab1.configure(background=settings.colours["primary"])
                self.tab2.configure(background=settings.colours["primary"])
                self.tab3.configure(background=settings.colours["primary"])
                confirm_primary.configure(background=settings.colours["primary"])
                self.volume_slider.configure(background= settings.colours["primary"])
                self.song_label.configure(background=settings.colours["primary"])
                self.volume_frame.configure(background=settings.colours["primary"])
                self.progress_bar.configure(background=settings.colours["primary"])
                self.buttonFrame.configure(background=settings.colours["primary"])

        def change_secondary_colour():
            old_colour = settings.colours["secondary"]
            data = secondaryEntry.get().replace(' ', '')
            settings.change_secondary(data)
            if settings.is_colour_valid(data):
                style.map("TNotebook", background=[("selected", settings.colours["secondary"])])
                style.configure("TNotebook.Tab", background=settings.colours["secondary"])
                self.volume_label.configure(background=settings.colours["secondary"])
                self.volume_slider.configure(troughcolor=settings.colours["secondary"])
                self.progress_bar.configure(troughcolor=settings.colours["secondary"])

                for widget in self.buttonFrame.winfo_children():
                    widget.configure(background=settings.colours["secondary"])

                for widget in self.tab1.winfo_children():
                    if widget.cget("background") == old_colour:
                        widget.configure(background=settings.colours["secondary"])

                for widget in self.tab2.winfo_children():
                    if widget.cget("background") == old_colour:
                        widget.configure(background=settings.colours["secondary"])

                for widget in self.tab3.winfo_children():
                    if widget.cget("background") == old_colour:
                        widget.configure(background=settings.colours["secondary"])

        settings_label = tk.Label(self.tab3, text="Settings", font=("Comic Sans", 13),
                                  background=settings.colours["secondary"])
        settings_label.place(x=150, y=10)
        primary_label = tk.Label(self.tab3, text="Primary Colour", font=("Comic Sans", 8),
                                 background=settings.colours["secondary"])
        primary_label.place(x=50, y=60)
        secondary_label = tk.Label(self.tab3, text="Secondary Colour", font=("Comic Sans", 8),
                                   background=settings.colours["secondary"])
        secondary_label.place(x=33, y=90)

        confirm_primary = tk.Button(self.tab3, text="Confirm", font=("Comic Sans", 8),
                                    background=settings.colours["primary"], command=change_primary_colour)
        confirm_primary.place(x=230, y=55)
        confirm_secondary = tk.Button(self.tab3, text="Confirm", font=("Comic Sans", 8),
                                      background=settings.colours["secondary"], command=change_secondary_colour)
        confirm_secondary.place(x=230, y=90)

    def play(self, file):
        if file != 0:
            media = vlc.Media(file)
            self.player.set_media(media)
        self.player.play()
        song_name = self.music_queue.get_current_song_name()[:-3]
        if len(song_name) > 60:
            song_name = song_name[:57] + "..."
        self.song_name.set(song_name)

        self.update_progress()

    def skip_forward(self):
        self.pause()
        self.music_queue.next_item()
        self.play(self.music_queue.display_playing_track())

    def skip_backward(self):
        self.pause()
        self.music_queue.last_item()
        self.play(self.music_queue.display_playing_track())

    def pause(self):
        self.player.pause()

    def backward(self):
        self.player.set_time(self.player.get_time() - 5000)

    def forward(self):
        self.player.set_time(self.player.get_time() + 5000)

    def update_progress(self):
        # Get the current position of the music
        current_position = self.player.get_position()
        # If the user is not actively dragging the scale, update it
        if not self.dragging:
            self.progress_bar.set(current_position * 100)
        # Call the update_progress function again after a certain amount of time
        self.after(100, self.update_progress)

    def on_scale_drag_start(self):
        self.dragging = True

    def on_scale_drag(self):
        if self.dragging:
            new_position = self.progress_bar.get() / 100
            self.player.set_position(new_position)
            self.player.play()

    def on_scale_drag_end(self):
        if self.dragging:
            self.dragging = False
            new_position = self.progress_bar.get() / 100
            self.player.set_position(new_position)

    def set_volume(self, volume):
        v = int(volume)
        self.player.audio_set_volume(v)

if __name__ == '__main__':
    app = MyApp()
    app.mainloop()
