Basic:

Repo structure:  
mini-project2/  
├── networking/  
│   ├── tempest/  
│   ├── mastermind/  
├── xv6/  
│   ├── user/  
│   ├── kernel/  
│   ├── Makefile  
│   └── ...  
├── ai-usage.md  
└── readme.md

Important:  
Monolithic code isnt allowed  
Allowed networking API: Only the raw POSIX sockets interface: socket, bind, listen, accept, connect, send, sendto, recv, recvfrom, setsockopt, getsockopt, getaddrinfo, shutdown, close, and poll, select or epoll.  
Banned: Any library that implements HTTP, a reliable datagram protocol, or message framing for you. This includes libcurl, libevent, libuv, ZeroMQ, ENet and anything similar. Shelling out to curl, wget or nc is also banned.

NETWORKING PORTION  
A-tempest

Input of form: tempest city\_name \--raw  
Here raw is optional flag  
We need to convert city\_name to url compatible form. 

Possible errors:  
Invalid syntax (Too many args is one)  
Invalid location  
Short reads and writes can be an issue (send() sends less packets then expected)  
TCP does not preserve application-level message boundaries, 1 send \!= 1 recv

CRLF struct the make http request  
GET /Hyderabad?0T HTTP/1.1\\r\\n  
Host: wttr.is\\r\\n  
Connection: close\\r\\n  
\\r\\n

Connection close needed  
10 sec timeout

For \--raw, we print bytes received by socket \-\> response buffer might be needed  
basic HTTP response parsing  
Is chunk encoding needed?

B. MAstermind  
peer-to-peer Mastermind game over a LAN  
Symbols: x- Correct digit and correct position  
o- Correct digit, wrong position

- \- Digit does not occur in master sequence

Max 12 attempts, repeated digits allowed  
Feedback out of order  
Both programs (client and server ) are 1 executable (either can be client or server, not fixed roles)

UDP discovery required  
Terminal is the ui  
Threads not required

1. Player discovery: discovery uses UDP, while actual game uses TCP. UDP needs a 4 dute magic identifier; so magic identifier|name|TCP listening port  (we shall have sender IP from UDP).   
2. Starting the game: We need a player table to update player details in; every 5 secs if not refreshed, remove from player table. Each player broadcasts every 5 secs. To start challenge send challenge ID. one who sends in mastermind and other is code breaker. TCP connection is sent, accepted by yes, rejected by no. (syn,syn-ack,ack, to establish connection). We establish one TCP connection which must remain open. Its bi directional.   
3. Game play: TCP send byte stream, how to demarkate the start and end of a msg?? (using \\n ?), validating msgs  
4. Game end: close tcp, back to homepage, and udp  
5. Failure(network disconnect): back to homepage/UDP discover  
6. Cost cutting mode: flag \--cost-cutting, UDP for game state, breaking into chunks, sending and reordering, ACK and retransmitting  
7. Logging: flag \--log, put all events in log.txt, code given to generate timestamp for log 

XV6 PORTION:

1. Copy-on-write fork: make separate page for child, only when child write, reference counting(dont close page, just cause 1 is done using, others might still be using)  
2. Alarms: handler acting like interrupting func call, kernel must not call the handler again while the previous handler is still running.

GENERAL INSTRUCTIONS:  
The boilerplates for networking and xv6 portion are provided to you. Don’t make changes to networking portions unless absolutely necessary. We are supposed to make changes to the xv6 portion.   
Make sure not only to fulfill every requirement, but keep a detailed log of the sequence in which you made every implementation, how you fulfilled a requirement, what changes you made in what file. I need to remake the project you create on my own, making periodic git commits, therefore I require full knowledge of what is being added, why, in what order, and how to test working of code at that stages. Design choices and assumptions must be explicitly stated.

ISSUE:  
Alright, before I start building I gotta confirm something with you. I own an apple silicon m5 pro mac book. The last osn project I had, it was made to be implemented on linux, so I had alot of issues. Does this project also have something where it can only be best implemented in linux? If so, I would like to pursue remedies before I start building. for eg my ta sent this msg: Yeah also one thing for mac users before submission you guys have to run your code it cannot happen that you come to the evals be like mac issue code doesn't run , try a docker or subsystems (distrobox) or if nothing just setup a GitHub codespace that's a Linux environment run it there but it cannot be acceptable to not be able to run your code at all

I am leaning towards using docker with an Ubuntu ARM64 image. Would this be the best choice or distrobox or GitHub Codespaces or some other resource?  
