from fabric import Connection
from ollama import Client

    
#to do command loop


#don't run this on a server and let people access it remotely, I'm pretty sure you can RCE by doing an command escape on ssh.run(cmd)

#this version of the program can't run a full  TTY so some commands can't be run in certain environments 

#original version that uses fabric for connections, uses a local ollama server for connections, you need to also run "ollama serve" if you've not already



#function that executes the command on the privesc target, edit this to change where the code is executed
#input format: exact string that you want to execute
#output format: command result or error
#in this case I've also added the ssh struct in input to simplify the code
def exec_command(cmd, ssh):
    try:
        ssh.run(cmd)
    except Exception as error: 
        print("the following error has occured" + str(error))
        return error



def human_cmd_validation(cmd, ssh):
    inp = input("the ai wants to run the following cmd, enter y/n confirm: \n" + cmd)
    if (inp.lower() == 'y'):
        exec_command(cmd, ssh)
    

def epilogue(ssh):
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
def prompt(message):
    #prompts the ai model
    response = client.chat(model='qwen2:7b', messages=[
        {
            'role': 'user',
            'content': message,
        },
    ])

    print(response.message.content)

    return response.message.content

    



if __name__ == "__main__":
    

     
    #temporarily like this, can add user input,
    user = 'oliver'
    #IPv6 host addresses are incompatible with the host:port shorthand 
    host = '10.10.11.80'
    password = 'theEd1t0rTeam99'

    #establishes ssh connection
    #the capitcal c in connection is important
    ssh = Connection(
        host= host,
        user= user,
        connect_kwargs={
            "password": password,
        },
    )

    #basic enumeration
    id = ssh.run('whoami')
    groups = ssh.run('id')
    hostname = ssh.run('hostname')

    #sudo doesn't work for some reason??????
    #sudo_l = ssh.run('sudo -l')

    release = ssh.run('cat /etc/os-release')
    base_prompt =""

    # prompt( base_prompt + "are there any privelige escalation vulnerabilites in the following release" + release)
    vuln_exists = prompt( base_prompt + "are there any privelige escalation vulnerabilites in the following release, ANSWER ONLY WITH yes or no" + release.stdout)
    command_prompt = "Give exactly ONE Linux command that could be used to attempt privilege escalation.Output only the raw command, nothing else."
    #if vuln_exists.lower() == "yes":
    if True:
        final_prompt = base_prompt + release.stdout + command_prompt
        cmd = prompt(final_prompt)
        human_cmd_validation(cmd, ssh)

    #closes the ssh connection

    epilogue(ssh)
