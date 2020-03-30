# Chat-Server
Chat Server by Python Sockets

A client/server chat application uses Python Socket Programming and Multi-Threading. Message codes and answers:

    | Messsage    	  | Answer 		|
    | ------ 		  | ------	 	|
    | RG nick:pass    | RO nick 	| (sign in)
    | RG nick:pass    | RN nick 	| (nickname already exists)
    | US nick:pass    | UO nick 	| (log in)
    | US nick:pass    | UN nick 	| (wrong password)
    | US nick:pass    | UR nick 	| (not existing user)
    | TI 		| TO 			| (to check connection)
    | QU 		| BY nick 	| (quit)
    | LQ		| LA nick:nick| (display online users)
    | CP oldpass:pass | CO			| (change password)
    | CP oldpass:pass | CN 			| (invalid password)
    | GM message 	  | GO 			| (send message to all)
    | PM nick:message | PO 			| (send pivate message to nick)
    | PM nick:message | PN nick 	| (not existing nick)
    | ER 			  | 			| (not existing command)
    | EL 			  | 			| (not logged in)
