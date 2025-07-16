class lidarConfigurationTool:

    def __init__():
        pass

        #opening

        #find lidar


        #baudrate

        #get trans


        #deadband

        #verbose checks

            #speed
            #id checks
            #auto start + connect
            #debug 
            #time
            #out


        #name

        #file write

        #test


        #quickstart tool??????

    def opening():
        print("Welcome the Wired lib lidar Config tool. If at any time you are confused type \"help\" and more information will be provided. Make sense? (y/n)")
        response = input().strip().lower()
        
        if response=='help':
            print("throughout the tool the character \'y\' will be used for yes and the character \'n\' will be used for no. If these responses are not working make sure your typing in lower case and then restart the tool.")

        elif response=="y":
            return
        
        elif response=="n":
            print("Try typing \"help\" for help")

        else:
            print("Sorry", response, "is not a valid response. Try y, n, or help. ")






if __name__ == '__main__':
    lidarConfigurationTool()