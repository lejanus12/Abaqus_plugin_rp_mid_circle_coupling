from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
import shutil


thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

# Construct the path to the directory one level above thisDir with the name '_rsgTmpDir'
directory_path = os.path.join(os.path.dirname(thisDir), '_rsgTmpDir')

# Check if the directory exists before attempting to remove it
if os.path.exists(directory_path):
    shutil.rmtree(directory_path)


toolset.registerGuiMenuButton(
    buttonText='Simbased tools|RP maker mid circles', 
    object=Activator(os.path.join(thisDir, 'rp_makerDB.py')),
    kernelInitString='import rp_maker',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=['Assembly','Step','Interaction', 'Load'],
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
