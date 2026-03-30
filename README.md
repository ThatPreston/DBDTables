# DBDTables

DBDTables is a tool that automatically generates up-to-date cosmetic datatables for Dead By Daylight. It was made to simplify the process of adding new cosmetics to the [Official DBD Wiki](https://deadbydaylight.wiki.gg/).

This tool is not affiliated with or endorsed by Behaviour Interactive, and all files accessed by it belong to their respective owners. Users must own a copy of the game for the tool to generate any derivative data.

You may need to add the folder containing this tool as an exclusion in your antivirus settings due to false positives.

## Configuration

> #### Required
> `dbdVersion`<br>
> Set this to the current version of Dead By Daylight you have installed, including the branch.<br>
> Examples: `9.5.1_live` or `9.5.0_ptb`<br><br>
> `paksFolder`<br>
> Set this to your `DeadByDaylight/Content/Paks` folder location.<br><br>
> `mappingFile`<br>
> Set this to your `.usmap` mapping file location.<br>
>
> #### Optional
> `enabledLanguages`<br>
> A list of languages to localize the datatables to.

## Usage

- Open `DBDTables.exe`
- Configure your Paks Folder and Mapping File paths (you can usually find updated mappings [here](https://github.com/Masusder/FModel-DbdMappings))
- Click "Export Game Files" (you only need to do this once unless the game updates or you delete the files)
- Click "Generate Datatables"
- The generated files should be located in the output folder!

Note: After installing or updating Dead By Daylight, you must allow it to fully load at least once for certain files to update.

![](https://i.gyazo.com/cd2d3878cd1d1910058f442a586f4991.png)

## Credits

- CUE4Parse for making it possible to automatically export the needed game files
- Masusder for creating the asset decryption algorithm and fixing it for newer game versions
- Official DBD Wiki folks for giving helpful feedback and notes on this

## Details

This tool was created in PyCharm and compiled using Nuitka. Releases include a `libraries` folder containing `CUE4Parse.dll` and its dependencies, which were obtained by cloning the [CUE4Parse repository](https://github.com/FabianFG/CUE4Parse) and building with the following added properties:
```
    <CopyLocalLockFileAssemblies>true</CopyLocalLockFileAssemblies>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
```
To run the source code, you will need Python 3.13, pythonnet, pycryptodome, and the aforementioned `libraries` folder.