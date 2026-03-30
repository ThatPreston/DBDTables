from pathlib import Path
import threading
import Config
from core import GameFileExporter, DatatableGenerator
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

print("Loading DBDTables...")

title = "DBDTables"
root = Tk()
root.title(title)
root.rowconfigure(0, weight = 1)
root.columnconfigure(0, weight = 1)

status = StringVar(value = "You must export game files at least once for this tool to work! After that, you only need to do it again if the game updates.")

calibri = ("Calibri", 12)
style = ttk.Style()
style.configure("Custom.TButton", font = calibri)
style.configure("Custom.TLabel", font = calibri)
style.configure("Custom.TEntry", font = calibri)

frame = ttk.Frame(root, padding = (16, 16, 16, 16))
frame.grid(column = 0, row = 0, sticky = "nsew")
frame.columnconfigure(0, weight = 1)
frame.rowconfigure(2, weight = 1)

options = ttk.Frame(frame)
options.grid(column = 0, row = 1, pady = (0, 8), sticky = "ew")
options.columnconfigure(1, weight = 1)

versionVar = StringVar(value = Config.gameVersion)
versionContainer = ttk.Frame(options)
versionContainer.grid(column = 1, row = 0, pady = (0, 8))
ttk.Label(versionContainer, text = "Game Version", style = "Custom.TLabel", width = 12, anchor = "center").grid(column = 0, row = 0, padx = (0, 4))
versionEntry = ttk.Entry(versionContainer, textvariable = versionVar, width = 12, font = calibri, justify = "center")
versionEntry.grid(column = 1, row = 0, padx = (4, 0), sticky = "w")

paksVar = StringVar(value = Config.paksFolder)
ttk.Label(options, text = "Paks Folder", style = "Custom.TLabel", width = 12, anchor = "center").grid(column = 0, row = 1, padx = (0, 8))
paksEntry = ttk.Entry(options, textvariable = paksVar, width = 50, state = "readonly", font = calibri)
paksEntry.grid(column = 1, row = 1, sticky = "ew")
paksButton = ttk.Button(options, text = "Browse", style = "Custom.TButton", width = 12)
paksButton.grid(column = 2, row = 1, padx = (8, 0))

mappingVar = StringVar(value = Config.mappingFile)
ttk.Label(options, text = "Mapping File", style = "Custom.TLabel", width = 12, anchor = "center").grid(column = 0, row = 2, padx = (0, 8))
mappingEntry = ttk.Entry(options, textvariable = mappingVar, width = 50, state = "readonly", font = calibri)
mappingEntry.grid(column = 1, row = 2, sticky = "ew")
mappingButton = ttk.Button(options, text = "Browse", style = "Custom.TButton", width = 12)
mappingButton.grid(column = 2, row = 2, padx = (8, 0))

buttons = ttk.Frame(options)
buttons.grid(column = 1, row = 3, sticky = "ew", pady = (8, 0))
buttons.columnconfigure(0, weight = 1)
buttons.columnconfigure(1, weight = 1)

exportButton = ttk.Button(buttons, text = "Export Game Files", style = "Custom.TButton", width = 20)
exportButton.grid(column = 0, row = 3, padx = (0, 4), sticky = "ew")

generateButton = ttk.Button(buttons, text = "Generate Datatables", style = "Custom.TButton", width = 20)
generateButton.grid(column = 1, row = 3, padx = (4, 0), sticky = "ew")

statusLabel = ttk.Label(frame, textvariable = status, style = "Custom.TLabel", anchor = "center", justify = "center", padding = (8, 8, 8, 8), wraplength = 500, relief = "groove")
statusLabel.grid(column = 0, row = 2, pady = (0, 8), sticky = "nsew")

progressBar = ttk.Progressbar(frame, orient = "horizontal", mode = "determinate")
progressBar.grid(column = 0, row = 3, sticky = "ew")

def toggleButtons(enabled):
    exportButton.configure(state = "enabled" if enabled else "disabled")
    generateButton.configure(state = "enabled" if enabled else "disabled")
    paksButton.configure(state = "enabled" if enabled else "disabled")
    mappingButton.configure(state = "enabled" if enabled else "disabled")
    versionEntry.configure(state = "enabled" if enabled else "readonly")
    root.focus()

# No point in allowing other branches since users can't install them
validBranches = ["live", "ptb"]

def validateVersion(versionString):
    s = versionString.split("_")
    if len(s) == 2:
        version = s[0]
        branch = s[1]
        if branch in validBranches:
            versionComponents = version.split(".")
            if len(versionComponents) == 3:
                for component in versionComponents:
                    if not component.isnumeric():
                        return False
                return True
    return False

def exportFiles():
    status.set("Initializing CUE4Parse...")
    try:
        GameFileExporter.init()
        status.set("Reading access keys...")
        Config.accessKeys.update(GameFileExporter.readAccessKeys())
        Config.save()
        status.set("Searching for game files...")
        totalFiles = GameFileExporter.populateExportList()
        progressBar.configure(mode = "determinate", maximum = totalFiles)
        status.set("Exporting necessary files...")
        GameFileExporter.exportFiles(progressBar.step)
        status.set("Game files exported!")
    except Exception as e:
        status.set(f"Exception: {str(e)}")
    toggleButtons(True)

def exportFilesButtonCommand():
    paksFolder = Path(paksVar.get())
    if not (paksFolder.is_dir() and str(paksFolder).endswith("DeadByDaylight\\Content\\Paks")):
        status.set("Invalid paks folder!")
        return
    mappingFile = Path(mappingVar.get())
    if not (mappingFile.is_file() and mappingFile.suffix == ".usmap"):
        status.set("Invalid mapping file!")
        return
    Config.paksFolder = str(paksFolder)
    Config.mappingFile = str(mappingFile)
    toggleButtons(False)
    thread = threading.Thread(target = exportFiles)
    thread.start()

def generate():
    success = DatatableGenerator.generate(status.set)
    if success:
        status.set("Successfully generated " + str(len(Config.enabledLanguages)) + " localized datatables!")
        Config.save()
    progressBar.stop()
    progressBar.configure(mode = "determinate")
    toggleButtons(True)

def generateButtonCommand():
    validVersion = validateVersion(versionVar.get())
    if not validVersion:
        status.set("Invalid game version!")
        return
    Config.gameVersion = versionVar.get()
    toggleButtons(False)
    progressBar.configure(mode = "indeterminate", maximum = 100)
    progressBar.start(10)
    thread = threading.Thread(target = generate)
    thread.start()

exportButton.configure(command = exportFilesButtonCommand)
generateButton.configure(command = generateButtonCommand)

paksEntry.xview_moveto(1)
mappingEntry.xview_moveto(1)

def browsePaksFolder():
    directory = filedialog.askdirectory(title = "Select Paks Folder", initialdir = "/")
    if len(directory) > 0:
        paksVar.set(directory)
        paksEntry.xview_moveto(1)

def browseMappingFile():
    path = filedialog.askopenfile(title = "Select Mapping File", filetypes = [("Mapping files", "*.usmap")], initialdir = "/")
    if path is not None:
        mappingVar.set(path.name)
        mappingEntry.xview_moveto(1)

paksButton.configure(command = browsePaksFolder)
mappingButton.configure(command = browseMappingFile)

def clear_focus(event):
    widget = event.widget
    if not isinstance(widget, Entry):
        root.focus()
    if widget != paksEntry:
        paksEntry.xview_moveto(1)
    if widget != mappingEntry:
        mappingEntry.xview_moveto(1)

root.bind("<Button-1>", clear_focus)

root.update_idletasks()
root.attributes("-topmost", True)
width = root.winfo_width()
height = root.winfo_height()
root.minsize(width, height)
x = int(root.winfo_screenwidth() / 2) - int(width / 2)
y = int(root.winfo_screenheight() / 2) - int(height / 2)
root.geometry(f"+{x}+{y}")

root.mainloop()