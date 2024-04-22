#
# expected output in terrarium: fail
#
import subprocess

result = subprocess.run('bash echo "test"', shell=True, text=True)

print(result)
