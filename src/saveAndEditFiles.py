import json 
import sys 
src = sys.argv[1]
dst = sys.argv[2]

print (src)
print(dst)

with open(src , 'r', encoding='utf-8') as f:
    data = json.load(f)

if "id" in data : 
    data["user_id"] = data.pop("id")

with open(dst , 'w', encoding='utf-8') as f:
    json.dump(data ,f , indent=2)


print(f"saved to {dst}")

# f = open(src)
# id_content = f.read()
# f.close()

# id_content = id_content.replace('id', 'user_id')