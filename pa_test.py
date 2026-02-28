import requests
token = "39f50dc9520994221f32ea0c96da060d5929c0ba"
headers = {"Authorization": f"Token {token}"}
users = ["MuthamiM", "muthamim", "muthami", "musamwange", "musamwange2", "Admin"]
for user in users:
    r = requests.get(f"https://www.pythonanywhere.com/api/v0/user/{user}/cpu/", headers=headers)
    if r.status_code == 200:
        print("FOUND USER:", user)
        break
    else:
        print(f"Failed for {user}: {r.status_code}")
