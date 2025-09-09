with open('otp_generator.py', 'r') as f:
    content = f.read()

content = content.replace('    \n\n    \n', '    \n')

with open('otp_generator.py', 'w') as f:
    f.write(content)

print('File updated')