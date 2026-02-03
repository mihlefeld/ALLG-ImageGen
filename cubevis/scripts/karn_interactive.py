from cubevis.scripts.karnotation import karnaukh_to_standard

algs = []
while True:
    try:
        user_input = input("Add alg or confirm:")
        if user_input == "":
            for alg in algs:
                orientation = alg.split("\t")[0]
                karn_alg = alg.split("\t")[1]
                print(orientation + "]", karnaukh_to_standard(karn_alg))
                print(alg)
            algs = []
        else:
            algs.append(user_input)
        
    except Exception as e:
        algs = []
        print(e)
