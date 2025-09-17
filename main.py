from fabric import Connection
from ollama import Client
#from pexpect import pxssh



#roadmap get full tty shell-> 
#roadmap get the command history system online -> RAG system online -> get full list of things to check online
#roadmap add file logs to the command loop
#roadmap save commands tried to log file
#add to lists of things to check


#don't run this on a server and let people access it remotely, I'm pretty sure you can RCE by doing an command escape on ssh.run(cmd)




#Constants
const_base_prompt ="You are an experience pen tester helping his junior analyst do an easy HTB box"
const_validation_failure_response = "system message: human did not allow this command to be run"

#global variables
system_info = "system info: "
command_log = " list of all the commands ran so far: \n"


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





def command_loop(vuln_type):
    give_up_response = "I give up"
    command_prompt = "Give exactly ONE Linux command that could be used to attempt privilege escalation.Output only the raw command, nothing else."
    loop_prompt = f"you have been given ten chances to execute commands to become the root user, if you want to give up early type exactly \"{give_up_response}\" "
    command = ""
    result = ""
    human_feedback = ""
    global system_info
    global command_log

    for i in range(10):
        if has_root():
            return "success"
        else:
            loop_prompt = (const_base_prompt + command_prompt + f"type of vulnerability currently in focus: {vuln_type}" +  " system info: " + system_info + command_log)
            print(loop_prompt)
            #prompts the ai model
            ai_response = prompt(loop_prompt, "gpt-oss:20b")
                if ai_response == give_up_response:
                break
            else:
                #puts the ai generate command to the human for validation then runs it 
                command = ai_response
                result = human_cmd_validation(ai_response)
                human_feedback = input("any feedback on the last command?")
                #logs the command, output, and pentester feedback
                command_log += f"turn : {str(i)}, command ran : {command},result : {result}, human_feedback : {human_feedback} \n"


#inputs cmds is a list of commands,
#prompt is a prompt it uses for ai model stuff

def enumerate_area(cmds, prompt_addition, vuln_type):
    const_more_info = "I want more info" 
    const_cmd_loop_affirmation = "proceed to command loop"
    global system_info

    #executes the normal 
    for cmd in cmds:
        system_info += f"command : {cmd} result : {exec_command(cmd)}"


    
    for i in range(5):
        enum_prompt = f"based on the following information, do you think that there are any {vuln_type} vulnerabilities for privelige escalation on the system? if you think there are vulns and want to run commands on the system for privesc please include \"{const_cmd_loop_affirmation}\"  if you want to run commands to gain additional system information please include exactly \"{const_more_info}\" in your response \n {system_info}, {prompt_addition}"
        enum_response = prompt(enum_prompt, "gpt-oss:20b")
        
        #runs the command loop agent if theai wants it 
        if (const_cmd_loop_affirmation.lower() in enum_response.lower()):
            command_loop(vuln_type)
            break
        #if the ai wants to run a command to get more info it lets it run that command and adds the info to the doc
        elif (const_more_info.lower() in enum_response.lower()): 
            more_info_prompt = f"what additional information do you want that is not covered in the following system information, INCLUDE ONLY the command you want run on the privesc target and nothing else. \n {system_info} \n here's what you said before {enum_response}"
            more_info_command = prompt(more_info_prompt, "gpt-oss:20b")
            more_info_result = human_cmd_validation(more_info_command)
            system_info += f"command : {more_info_command} result : {more_info_result}"

    

    
if __name__ == "__main__":
    
    create_connection()


    basic_info = ["whoami", "id", "sudo -l", "ifconfig", "echo $path", "env"]
    test_prompt = "look through this information carefully"
    enumerate_area(basic_info, test_prompt, "general system setup")

    


    #release = 'PRETTY_NAME=/"Ubuntu 22.04.5 LTS/"NAME=/"Ubuntu/" VERSION_ID=/"22.04/" VERSION=/"22.04.5 LTS (Jammy Jellyfish)/" '

    
    
    vuln_find_prompt =  "are there any privelige escalation vulnerabilites in the following release, ANSWER ONLY WITH yes or no"
    # prompt( base_prompt + "are there any privelige escalation vulnerabilites in the following release" + release)
    #vuln_exists = prompt( (const_base_prompt + vuln_find_prompt + release), "gpt-oss:20b")
    

    
    #if vuln_exists.lower() == "yes":
        #final_prompt = const_base_prompt + release + command_prompt
        #cmd = prompt(final_prompt,"qwen2:7b")
        #print(cmd)
        
    #closes the ssh connection

    epilogue()
