
import pickle
def main():
    f = open('tags.txt','rb')
    fw = open('tags_text.csv','w')
    taghash= pickle.load(f)
    f.close()
    # print(taghash)
    for k,v in taghash.iteritems():
        # # print "dict[%s]=" % k,v
        fw.write(k)
        fw.write(',')
        fw.write(v[0])
        fw.write(',')
        fw.write(v[1])
        fw.write("\n")

    fw.close()
if __name__ == '__main__':
    main()
