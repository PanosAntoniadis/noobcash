# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os

from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from time import sleep



style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end


print('Initializing node...\n')
sleep(2)
print("Node initialized!\n")
while True:
    print("----------------------------------------------------------------------")
    method_q = [
        {
            'type': 'list',
            'name': 'method',
            'message': 'What would you like to do?',
            'choices': ['New transaction', 'View transactions', 'Show balance', 'Help', 'Exit'],
            'filter': lambda val: val.lower()
        }]
    method_a = prompt(method_q, style=style)["method"]
    os.system('cls||clear')
    if method_a == 'new transaction':
        print("New transaction!")
        print("----------------------------------------------------------------------")
        transaction_q = [
            {
                'type': 'input',
                'name': 'receiver',
                'message': 'Receiver (type receiver\'s id):',
                'validate': NumberValidator,
                'filter': lambda val: int(val)
            },
            {
                'type': 'input',
                'name': 'amount',
                'message': 'Amount:',
                'validate': NumberValidator,
                'filter': lambda val: int(val)
        }]
        transaction_a = prompt(transaction_q, style=style)
        print("\nConfirmation:")
        confirmation_q = [
            {
                'type': 'confirm',
                'name': 'confirm',
                'message': 'Do you want to send '+str(transaction_a["amount"])+' NBCs to node '+ str(transaction_a["receiver"])+ '?',
                'default': False
            }
        ]
        confirmation_a = prompt(confirmation_q)["confirm"]
        if confirmation_a:
            print("\nTransaction succeeded!\n")
            HomeOrExit_q = [
                {
                    'type': 'list',
                    'name': 'option',
                    'message': 'What do you want to do?',
                    'choices': ['Home', 'Exit'],
                    'filter': lambda val: val.lower()
                }]
            HomeOrExit_a = prompt(HomeOrExit_q)['option']
            if HomeOrExit_a == 'exit':
                break
            else:
                os.system('cls||clear')
        else:
            print("\nTransaction aborted.")

    elif method_a == 'view transactions':
        print("Your transactions")
        print("----------------------------------------------------------------------")

    elif method_a == 'show balance':
        print("Your balance")
        print("----------------------------------------------------------------------")


    elif method_a == 'help':
        print("Help")
        print("----------------------------------------------------------------------")
        print("You have the following options:")
        print("- New transaction: Creates a new transaction. You are asked for the")
        print("  id of the node to which you want to send the NBCs and the amount of NBCs")
        print("  to send.")
        print("- View transactions: Prints the transactions of the last validated")
        print("  block of the noobcash blockchain.")
        print("- Show balance: Prints the current balance of your wallet.")
        print("- Help: Prints usage information about the options.\n")
        
        HomeOrExit_q = [
                {
                    'type': 'list',
                    'name': 'option',
                    'message': 'What do you want to do?',
                    'choices': ['Home', 'Exit'],
                    'filter': lambda val: val.lower()
                }]
        HomeOrExit_a = prompt(HomeOrExit_q)["option"] 
        if HomeOrExit_a == "exit":
            break
        else:
            os.system('cls||clear')

    else:
        break