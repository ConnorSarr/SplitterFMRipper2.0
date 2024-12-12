import requests, os, bs4, json

BASEPATH = os.path.dirname(os.path.realpath(__file__))

def getAudioFromLink(audioLink):
    playerReq = requests.get(audioLink)
    playerSoup = bs4.BeautifulSoup(playerReq.text, features='html.parser')
    
    scriptTags = playerSoup.find_all("script", string=True)
    theTag = ""
    for scriptTag in scriptTags:
        if("window.jsonVars = " in str(scriptTag)): #find the script tag with the song information
            theTag = str(scriptTag).replace("<script>window.jsonVars = ","").replace(";</script>","") #clean it up for when we make it a python JSON object
    
    songInfo = json.loads(theTag)
    
    artistName = songInfo['artist']['artistName']
    songName = songInfo['song']['name']
            
    artistFPath = os.path.join(BASEPATH,artistName)
    songFPath = os.path.join(artistFPath,f"{songName} - {artistName}")
    
    if os.path.exists(artistFPath) is False:
        os.makedirs(artistFPath)
    if os.path.exists(songFPath) is False:
        os.makedirs(songFPath)
        
    for stem in songInfo['stems']:
        try:
            stemName = f"{str(stem['originalFilename']).replace(".wav","").replace(".mp3","")}.mp3" if stem['originalFilename'] != "" else f"{str(stem['name']).replace(".mp3","")}.mp3"
        except:
            stemName = f"{str(stem['name']).replace(".mp3","")}.mp3" #get rid of the mp3 tag if it's there, and add it back ourselves (just adds it if no mp3 tag is already there)
        
        print(f"Downloading {stemName} for {songName} - {artistName}")
        stemDownload = requests.get(stem['audioUrl'],stream=True)
        with open(os.path.join(songFPath,stemName), "wb+") as stemFile:
            stemFile.write(stemDownload.content)
          

def getAllArtistLinks(artistLink):
    links = []
    
    artistSplit = artistLink.split("/")
    for i,linkPart in enumerate(artistSplit):
        if "splitter.fm" in linkPart:
            artistPageName = artistSplit[i+1]
            
    artistReq = requests.get(artistLink)
    artistSoupParse = bs4.BeautifulSoup(artistReq.text,features="html.parser")
    
    for a in artistSoupParse.find_all('a', href=True):
        link = f"https://splitter.fm{a['href']}"
        if "player" in link or artistPageName in link: #grabs only the public links, NO PATREON PROTECTED LINKS
            links.append(link)
    
    return links

def main():
    gotLink = False
    while not gotLink:
        inputlink = input("Enter a either an artist link or song link from splitter.fm: ")
        if("splitter.fm" not in inputlink): #basic check to see if the link is a splitter link
            print("Please enter a splitter.fm link!\n")
        else:
            gotLink = True
    
    #determine if link is a player or artist page
    if "player" in inputlink:
        artistLink = False
    else:
        with requests.get(inputlink, stream=True) as r:
            #check if the page is loading the audio player .js file into the webpage
            artistLink = True if "1025e96316613beaf102be30169b5d83fddd22dfb5ead29c9b1ae0892f263cd0.js" not in r.text else False
    
    if artistLink:
        links = getAllArtistLinks(inputlink)
    else:
        links = [inputlink]
    
    for audiolink in links:
        getAudioFromLink(audiolink)

if __name__ == "__main__":
    main()