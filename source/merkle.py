from hashlib import sha256

def hash2(a, b):
    return sha256(sha256(a + b).digest()).digest()

def hash_list(lst):
    newlst = []
    for l in lst:
        newlst.append(sha256(sha256(l.encode()).digest()).digest())
    return newlst

def merkle(hashList):
    if len(hashList) == 1:
        return hashList[0]
    newHashList = []
    for i in range(0, len(hashList)-1, 2):
        hash = hash2(hashList[i], hashList[i+1])
        newHashList.append(hash)
    if len(hashList) % 2 == 1:
        newHashList.append(hash2(hashList[-1], hashList[-1]))
    return merkle(newHashList)

def create_merkle_tree(root):
    hashList = hash_list(root)
    return merkle(hashList)

