import requests
import json


class BotList(object):
    def __init__(self):
        self.channelMinimum = 150
        self.daysMinimum = 30
        # self.lastOnline = time.time() - (self.daysMinimum * 24 * 60 * 60)
        self.bots = []

        with (open("whitelist.json") as file):
            self.whitelist = json.load(file)

        with (open("greylist.json") as file):
            self.greylist = json.load(file)

        with (open("blacklist.json") as file):
            self.blacklist = json.load(file)

        self.update()

    def update(self):
        self.bots = self.fetchList()

    def fetchList(self):
        url = "https://api.twitchinsights.net/v1/bots/all"
        response = requests.get(url)
        text = response.text

        data = json.loads(text)

        return self.filterList(data["bots"])

        # and int(b[2]) >= self.lastOnline

    def filterList(self, bots: dict):
        fbots = [
            b[0]
            for b in bots
            if int(b[1]) >= self.channelMinimum
            and b[0] not in self.whitelist
            and b[0] not in self.greylist
        ]
        fbots.extend(self.blacklist)
        return fbots

    def allow(self, user: str):
        if user not in self.whitelist:
            self.whitelist.append(user)
        if user in self.blacklist:
            self.blacklist.remove(user)
            with (open("blacklist.json", mode="w") as file):
                json.dump(self.blacklist, file, indent=4)
        with (open("whitelist.json", mode="w") as file):
            json.dump(self.whitelist, file, indent=4)
        self.update()

    def disallow(self, user: str):
        if user not in self.blacklist:
            self.blacklist.append(user)
        if user in self.whitelist:
            self.whitelist.remove(user)
            with (open("whitelist.json", mode="w") as file):
                json.dump(self.whitelist, file, indent=4)
        with (open("blacklist.json", mode="w") as file):
            json.dump(self.blacklist, file, indent=4)
        self.update()

    def remove(self, user: str):
        if user in self.blacklist:
            self.blacklist.remove(user)
            with (open("blacklist.json", mode="w") as file):
                json.dump(self.blacklist, file, indent=4)
        if user in self.whitelist:
            self.whitelist.remove(user)
            with (open("whitelist.json", mode="w") as file):
                json.dump(self.whitelist, file, indent=4)
        self.update()

    def count(self):
        return len(self.bots)

    def ToList(self):
        return list(self.bots)
