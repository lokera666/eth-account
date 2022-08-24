from replit import db

i = 0
for entry in db.keys():
  print(entry)
  i += 1

print(i)