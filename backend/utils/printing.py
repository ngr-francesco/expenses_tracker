def print_dict_in_dict(dictionary, init_msg= ''):
    print(init_msg)
    for key,value in dictionary.items():
        print(key,':')
        for k,v in value.items():
            print(f'\t{k}',v, sep=':\t')