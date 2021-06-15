# Surface Simulation
This program is surface interaction simulator, 
reformed and improved based on https://github.com/stanlo229/surface-simulation-goh-lab with permission.

## Installation of Python and Requirement Package

1. Install python
    * Open https://www.python.org/ to download the python and install.
    
2. Install required package
    * Open RequiredPackage.txt.
    * Using pip to install all requirement package, command shows below, XXX replaced by the package name:
    ```bash
    pip install XXX
    ```
    * If you do not have pip installed, make sure you download Python 2 or Python 3 from the official 
      website: https://www.python.org/downloads/

## Run the program

### prerequisite
1. The description of all parameter want user to input is illustrated in the file HelpFile.txt under folder TextFile.  
   User can open and read the meaning of all parameter put in at here or type help or click help when running the 
   program depends on how you run the program.  
   The format of HelpFile is: VariableName : Description

2. The special restriction of some variables are listed in the file SpecialRequirement.txt under folder TextFile.  
   The message listed in the file will appear on the screen if you type wrong parameter. The format of SpecialRequirement is :
   VariableName: Restriction : Checking condition  
   User don't need to understand the checking condition at the end.

3. The parameter change from the old version is listed in the file OldNewTransfer.txt.  
   If need to reproduce the result from the old version, please look at this file.

### Overview of the program
1. This program asked user to input some parameter showed in the next section.
2. Based on the user input, film and bacteria will be generated with domain on it, number of each depends on the simulation type.
3. (For now, will change in the future)  
   Program will use bacteria to scan the film surface and calculate the energy.
4. Result will be saved into an Excel file.


### Parameters illustrate
Coming soon


### Running simulation
1. Run by user input in command line:
   * In the terminal with correct directory of program code, type in 
     * (For macOS)
     ```bash
      python3 RunSimulationCmd.py
      ```
      * (For Windows)
      ```bash
      python3.exe RunSimulationCmd.py
      ```
   * Follow the promotion in the terminal to type in the corresponding value to start the simulation
   
2. Run by GUI (Coming soon)
   * In the terminal with correct directory of program code, type in 
     * (For macOS)
     ```bash
      python3 RunSimulationGUI.py
      ```
      * (For Windows)
      ```bash
      python3.exe RunSimulationGUI.py
      ```
     
   * Select the simulation you want in the windows and enter the corresponding simulation condition you want to start the simulation
   
3. Run by script (Coming soon)

### Result
Result of the simulation will be saved in the folder Result

### Extra Info
* The log of running will be saved under folder Log. If error happen, user may look at the log file to figure out the error.

* For more info, don't hesitate to contact me at **Jiaqi.gong@mail.utoronto.ca** with email title "Surface Simulation Troubleshooting"
   
