from Pyro4 import expose
from os import stat

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        strings = self.read_input()
        text = strings[len(strings) - 1]
        patterns = strings[:len(strings) - 1]
        n = len(patterns)
        step = n / len(self.workers)
        mapped = []
        for i in xrange(0, len(self.workers)):
            mapped.append(self.workers[i].mymap(i * step, (i + 1) * step, patterns, text))
        reduced = self.myreduce(mapped)
        self.write_output(reduced)

    @staticmethod
    @expose
    def mymap(a, b, patterns, text):
        res = []
        for i in xrange(a, b):
            inxs = Solver.getMatches(text, patterns[i])
            res.append({'Pattern': patterns[i], 'Occurencies': inxs})
        return res

    @staticmethod
    @expose
    def myreduce(mapped):
        res = []
        for chunk in mapped:
            for dict in chunk.value:
                res.append(dict)
        return res

    @staticmethod
    @expose
    def getMatches(text, pattern):
        occurencies = []
        pat_len = len(pattern)
        txt_len = len(text)
        i = 0
        j = 0
        pat_hash = 0
        txt_hash = 0
        h = 1
        q = 101
        d = 26
        for i in range(pat_len-1):
            h = (h * d) % q

        for i in range(pat_len):
            pat_hash = (d * pat_hash + ord(pattern[i])) % q
            txt_hash = (d * txt_hash + ord(text[i])) % q

        for i in range(txt_len - pat_len + 1):
            if pat_hash == txt_hash:
                for j in range(pat_len):
                    if text[i + j] != pattern[j]:
                        break
                    else:
                        j += 1

                if j == pat_len:
                    occurencies.append(i)
            if i < txt_len - pat_len:
                txt_hash = (d * (txt_hash - ord(text[i]) * h) + ord(text[i + pat_len])) % q
                if txt_hash < 0:
                    txt_hash += q
        return occurencies


    def read_input(self):
        f = open(self.input_file_name, 'r')
        return [line.strip() for line in f.readlines()]

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        for dict in output:
            if (len(dict['Occurencies']) == 0):
                continue
            f.write('Pattern: ' + dict['Pattern'] + '\n')
            f.write('Occurencies: ')
            for inx in dict['Occurencies']:
                f.write(str(inx) + ', ')
            f.write('\n\n')
        f.close()