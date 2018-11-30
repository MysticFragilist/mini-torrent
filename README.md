# turbo-torrent
A mini torrent system in CLI for linux and windows OS. The client using `./mtor-client.py` can download a file from multiple server entry point.

You can use the torrent with a file.mtr as follow:
```
some_file.txt
12345
10.0.2.4
10.0.2.8
10.0.2.78
...
```
A .mtr file must be formatted as above. It must start with the file name to download from the servers. Next line needs to be the size of the file in bytes. The following lines are for the servers IP in which the file could be.

### Usage
Servers need to run the file `./mtor-serveur.py` to makes the torrent working. From the server, the command needs to be called this way `./mtor-serveur.py fileServer/ 3000`. It must be followed by the **directory** in which the server will take his file from and the **port number** on which it needs to be run.


The client needs to launch `./mtor-client.py file.mtr 3000` followed by the **.mtr file** and the **port on the server** where the server is hosting itself.


### Features & Future upgrade
Some future feature that could be made:
- Make a **pickle** serializable for block sending
- Make a **loading screen** for a better visual
- Add more verification & bug fix




##### -- Copyright --
This project is protected by the MIT Licence.
This project has been done in an educational purpose for a class in TCP/socket at Bois-de-Boulogne college.
