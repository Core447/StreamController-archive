from urllib.parse import urlparse
from urllib.request import urlopen
import json, subprocess, os, shutil

class GitHubHelper:
    def getRaw(self, repoUrl: str, filePath: str, branchName: str = None, commitSHA: str = None):
        """
        Retrieves the raw content of a file from a given GitHub repository.

        Args:
            repoUrl (str): The URL of the GitHub repository.
            filePath (str): The path to the file.
            branchName (str, optional): The name of the branch. Defaults to None.
            commitSHA (str, optional): The SHA of the commit. Defaults to None.
            
            You can only provide one of branchName or commitSHA
            If you provide branchName the newest revision of the file will be fetched

        Raises:
            ValueError: If neither branchName nor commitSHA is specified.
            ValueError: If both branchName and commitSHA are specified.

        Returns:
            str: The raw content of the file.

        Example Usage:
            getRaw("https://github.com/user/repo", "path/to/file.txt", branchName="main")
        """
        if branchName == None and commitSHA == None:
            raise ValueError("Please specify branchName or commitSHA for the request")
        if branchName != None and commitSHA != None:
            raise ValueError("Please provide either branchName or commitSHA for the request")
        
        if branchName != None:
            identifier = branchName
            rawFileUrl = self.makeRawUrl(repoUrl, filePath, branchName=branchName)
        elif commitSHA != None:
            identifier = commitSHA
            rawFileUrl = self.makeRawUrl(repoUrl, filePath, commitSHA=commitSHA)

        # rawFileUrl = self.makeRawUrl(repoUrl, filePath, branchName=branchName, commitSHA=commitSHA)
        print(rawFileUrl)
        return urlopen(rawFileUrl).read()
    
    def makeRawUrl(self, repoUrl: str, filePath: str, branchName: str = None, commitSHA: str = None):
        """
        Generates a raw URL for accessing a file in a repository.

        Args:
            repoUrl (str): The URL of the repository.
            filePath (str): The path to the file.
            branchName (str, optional): The name of the branch. Defaults to None.
            commitSHA (str, optional): The SHA of the commit. Defaults to None.

            You can only provide one of branchName or commitSHA
            If you provide branchName the newest revision of the file will be used

        Raises:
            ValueError: If neither branchName nor commitSHA is provided.
            ValueError: If both branchName and commitSHA are provided.

        Returns:
            str: The raw URL of the file.
        """
        if branchName == None and commitSHA == None:
            raise ValueError("Please specify branchName or commitSHA for the request")
        if branchName != None and commitSHA != None:
            raise ValueError("Please provide either branchName or commitSHA for the request")
        
        rawFileUrl = repoUrl
        # Change url to raw.githubusercontent.com if not already done
        domain = urlparse(repoUrl).netloc
        if domain == "github.com":
            rawFileUrl = repoUrl.replace("github.com", "raw.githubusercontent.com", 1)
        
        # Add branch name or commit hash to url
        if branchName != None:
            rawFileUrl += "/"+branchName
        elif commitSHA != None:
            rawFileUrl += "/"+commitSHA
        
        rawFileUrl += "/"+filePath
        return rawFileUrl
    
    def cloneAtCommit(self, repoUrl: str, commitHash: str):
        """
        Clones a repository at a specific commit.
        """

        # Check if git is installed
        retval = subprocess.call(["which", "git"])
        if retval != 0:
            # Git is not installed on the system
            raise SystemError("Git is not installed on your system")
            return
        
        # Get name of repository
        projectName = repoUrl.split("/")[-1]

        # Remove folder in tmp/downloads
        shutil.rmtree(f"tmp/downloads/{projectName}", ignore_errors=True)

        # Clone the repository at the newest state
        subprocess.call(["git", "clone",  repoUrl, f"tmp/downloads/{projectName}"])

        # Add repository to the safe directory list to avoid dubious ownership warnings
        fullPath = os.path.abspath(f"tmp/downloads/{projectName}")
        subprocess.call(["git", "config", "--global", "--add", "safe.directory", fullPath])

        # Revert repository to the specified commit
        os.system(f"cd tmp/downloads/{projectName} && git reset --hard {commitHash}")

        # Install the plugin
        self.installPlugin(f"tmp/downloads/{projectName}", projectName)

    def installPlugin(self, pluginPath: str, folderName: str):
        """
        Installs a plugin from the given plugin path to the specified folder name.

        Parameters:
            pluginPath (str): The path of the plugin to be installed.
            folderName (str): The name of the folder where the plugin will be installed.

        Raises:
            TypeError: If pluginPath or folderName is not a string.

        Returns:
            None
        """
        if not isinstance(pluginPath, str):
            raise TypeError("pluginPath must be a string")
        if not isinstance(folderName, str):
            raise TypeError("folderName must be a string")
        
        # Install the plugin
        if os.path.isdir(f"tmp/downloads/{folderName}"):
            print(f"Warning: The plugin {folderName} already exists, continue anyway...")
            shutil.rmtree(f"tmp/downloads/{folderName}")
        # Copy plugin folder
        shutil.copytree(pluginPath, f"tmp/downloads/{folderName}")

    def downloadFile(self, repoUrl: str, repoFilePath: str, localFilePath: str, branchName: str = None, commitSHA: str = None):
        """
        Downloads a file from a given repository URL and saves it to a specified local file path.

        Args:
            repoUrl (str): The URL of the repository.
            repoFilePath (str): The path to the file within the repository.
            localFilePath (str): The path where the downloaded file will be saved.
            branchName (str, optional): The name of the branch to download the file from. Defaults to None.
            commitSHA (str, optional): The SHA of the commit to download the file from. Defaults to None.

        Raises:
            TypeError: If repoUrl, repoFilePath, or localFilePath are not strings.
            ValueError: If both branchName and commitSHA are None, or if both are provided.

        Returns:
            None
        """
        if not isinstance(repoUrl, str):
            raise TypeError("repoUrl must be a string")
        if not isinstance(repoFilePath, str):
            raise TypeError("repoFilePath must be a string")
        if not isinstance(localFilePath, str):
            raise TypeError("localFilePath must be a string")
        
        if branchName == None and commitSHA == None:
            raise ValueError("Please specify branchName or commitSHA for the request")
        if branchName != None and commitSHA != None:
            raise ValueError("Please provide either branchName or commitSHA for the request")
        
        fileContent = self.getRaw(repoUrl, repoFilePath, branchName=branchName, commitSHA=commitSHA)
        with open(localFilePath, "wb") as file:
            file.write(fileContent)

    def downloadThumbnail(self, repoUrl: str, remotePath: str, branchName: str = None, commitSHA: str = None):
        """
        Download a thumbnail image from a given repository URL and save it locally.

        Parameters:
            repoUrl (str): The URL of the repository.
            remotePath (str): The path to the remote thumbnail image.
            branchName (str, optional): The name of the branch to download the file from. Defaults to None.
            commitSHA (str, optional): The SHA of the commit to download the file from. Defaults to None.

        Returns:
            str: The local path where the downloaded thumbnail is saved.
            TypeError: If repoUrl, repoFilePath, or localFilePath are not strings.
            ValueError: If both branchName and commitSHA are None, or if both are provided.

        """
        if branchName == None and commitSHA == None:
            raise ValueError("Please specify branchName or commitSHA for the request")
        if branchName != None and commitSHA != None:
            raise ValueError("Please provide either branchName or commitSHA for the request")
        
        if not isinstance(repoUrl, str):
            raise TypeError("repoUrl must be a string")
        if not isinstance(remotePath, str):
            raise TypeError("remotePath must be a string")
        
        repoName = repoUrl.split("/")[-1]
        if not os.path.isdir("tmp/thumbnails"):
            os.mkdir("tmp/thumbnails")
        fileExtension = os.path.splitext(remotePath)[1]
        self.downloadFile(repoUrl, remotePath, f"tmp/thumbnails/{repoName}.{fileExtension}", branchName=branchName, commitSHA=commitSHA)

        return f"tmp/thumbnails/{repoName}.{fileExtension}"