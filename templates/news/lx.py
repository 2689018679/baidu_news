t=(
    (1,0),
    (2,0),
    (3,1)
)

# cj=[
#     {1:[{2:[],3:[{4:[]}]}]},
# ]

cj=[]

def fun(cj,id,u_id):
    if u_id==0:
        cj.append([id,[]])
        return
    for item in cj:
        if item[0]==u_id:
            item[1].append([id,[]])
        else:
            fun(item[1],id,u_id)

for id,u_id in t:
    if u_id ==0:
        fun(cj,id,u_id)

print(cj)