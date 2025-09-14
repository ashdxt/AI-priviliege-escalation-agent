from fabric import Connection
from ollama import Client
#from pexpect import pxssh



#roadmap get full tty shell->  implememnt has_root -> implement command loop -> figure out implementing different checks

    
#to do command loop
#to do error handling for commands


#don't run this on a server and let people access it remotely, I'm pretty sure you can RCE by doing an command escape on ssh.run(cmd)




#Constants
const_base_prompt ="You are an experience pen tester helping his junior analyst do an easy HTB box"
const_validation_failure_response = "system message: human did not allow this command to be run"



#function that executes the command on the privesc target, edit this to change where the code is executed
#input format: exact string that you want to execute
#output format: command result or error
#in this case I've also added the ssh struct in input to simplify the code
def exec_command(cmd):
    try:
        output = ssh.run(cmd, pty=True)
    except Exception as error: 
        print("the following error has occured" + str(error))
        return (str(error.result.stdout) )

    return output.stdout


#takes in command, if human gives confirmation, runs the command and then returns the output
#if no human validation returns const_validation_failure_response
def human_cmd_validation(cmd):
    inp = input("the ai wants to run the following cmd, enter y/n confirm: \n" + cmd)
    if (inp.lower() == 'y'):
        return exec_command(cmd)
    else:
        return const_validation_failure_response
    

def epilogue():
    print("succesfully executed program!")
    #ending closing all connections
    ssh.close

#ollama client delete if using chatgpt instead
client = Client(
    host='http://localhost:11434',
    headers={'x-some-header': 'some-value'}
)

#wrapper that prompts the ai model, feel free to replace with your own if you want to use some other ai model
#format: input : the prompt it wants to send to the ai model in the form of the string message
#output: returns the response of the ai model using the python function return
def prompt(message, model):
    #prompts the ai model
    response = client.chat(model=model, messages=[
        {
            'role': 'user',
            'content': message,
        },
    ])

    print(response.message.content)

    return response.message.content

def has_root():
    #figures out if root has been gained
    #need to make sure it actually works
    user = exec_command("whoami")
    print (user)
    if (user.lower() == "root\n"):
        return True
    else:
        return False




def create_connection():    
    #temporarily like this, can add user input,
    user = 'oliver'
    #IPv6 host addresses are incompatible with the host:port shorthand 
    host = '10.10.11.80'
    password = 'theEd1t0rTeam99'

    #establishes ssh connection
    #the capitcal c in connection is important
    global ssh
    ssh = Connection(
        host= host,
        user= user,
        connect_kwargs={
            "password": password,
        },
    )

def command_loop(system_inf):
    give_up_response = "I give up"
    command_prompt = "Give exactly ONE Linux command that could be used to attempt privilege escalation.Output only the raw command, nothing else."
    loop_prompt = f"you have been given ten chances to execute commands to become the root user, if you want to give up early type exactly \"{give_up_response}\" "
    prev_command = ""
    prev_result = ""
    
    human_feedback = ""
    
    for i in range(10):
        if has_root():
            return "success"
        else:
            loop_prompt = (const_base_prompt + command_prompt + "system info: " + system_inf + "previous command: "+ prev_command + "previous result: " + prev_result + "user feedback on last command:" + human_feedback)
            print(loop_prompt)
            ai_response = prompt(loop_prompt, "qwen2:7b")
            if ai_response == give_up_response:
                break
            else:
                prev_command = ai_response
                prev_result = human_cmd_validation(ai_response)
                human_feedback = input("any feedback on the last command?")







if __name__ == "__main__":
    

    create_connection()


    release = 'PRETTY_NAME=/"Ubuntu 22.04.5 LTS/"NAME=/"Ubuntu/" VERSION_ID=/"22.04/" VERSION=/"22.04.5 LTS (Jammy Jellyfish)/" '

    
    
    vuln_find_prompt =  "are there any privelige escalation vulnerabilites in the following release, ANSWER ONLY WITH yes or no"
    # prompt( base_prompt + "are there any privelige escalation vulnerabilites in the following release" + release)
    #vuln_exists = prompt( (const_base_prompt + vuln_find_prompt + release), "gpt-oss:20b")
    
    command_loop(release)
    
    #if vuln_exists.lower() == "yes":
        #final_prompt = const_base_prompt + release + command_prompt
        #cmd = prompt(final_prompt,"qwen2:7b")
        #print(cmd)
        
    #closes the ssh connection

    epilogue()
