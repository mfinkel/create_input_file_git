"""
this is supoast to load POLDI - data and create the correct inputfile.
the diameter of the sampel is nececarry to know.
"""
import os
import re
import numpy as np


class DataRead(object):
    def __init__(self, diameter):
        self.Data = DataContainer()
        self.sample_diameter = float(diameter)

    def save_data(self, filename, material="random"):
        header = "#Material: {} \n" \
                 "#Force:\t Phase:\t  hkl:\t phi:\tpsi:\tstrain:\t   strain error:\tstress:\t    stress error:\n".format(material)
        data = ""
        phase_keys = sorted(self.Data.data_dict.keys())
        for i, phase in enumerate(phase_keys):  # loop over all phases
            force_keys = sorted(self.Data.data_dict[phase].keys())
            print force_keys
            for j, force in enumerate(force_keys):
                phi_psi_hkl_list = self.Data.data_dict[phase][force][0]
                strain_stress_list = self.Data.data_dict[phase][force][1]
                for count in xrange(len(phi_psi_hkl_list)):
                    phi, psi, h, k, l = phi_psi_hkl_list[count]
                    strain, straind_err, stress, stress_err = strain_stress_list[count]
                    buffer = "{:4.1f}     {:>7}   {:1.0f} {} {}  {:2.0f}    {: 3.0f}     {: 1.7f}  {:1.7f}        " \
                             "{:9.0f}  {:9.0f}\n".format(
                        force, phase, h, k, l, phi, psi, strain, straind_err, stress, stress_err
                    )
                    data += buffer
        file = open(filename + ".dat", "w")
        file.write(header + data)
        file.close()


class LoadPOLDIData(DataRead):
    def __init__(self, diameter):
        super(LoadPOLDIData, self).__init__(diameter)
        self.load_data()

    def get_all_files(self):
        # print os.getcwd()
        main_dir_name = os.getcwd() + "\\data"
        dir_list = []
        for i in os.listdir(main_dir_name):  # loop over all folders containing the data under the different forces
            # print i
            new_path = main_dir_name + '\\' + i
            if os.path.isdir(new_path):
                force = self.pars_dirname(i)
                dir_list.append([new_path, force])
        # print dir_list
        f_list = []
        for i in xrange(len(dir_list)):
            dir_path = dir_list[i][0]
            force = dir_list[i][1]
            filelist = os.listdir(dir_path)
            # print "filelist", filelist
            for j in xrange(len(filelist)):
                f = dir_path + "\\" + filelist[j]
                if ("history" not in filelist[j]) and os.path.isfile(f):  #
                    phase, h, k, l = self.pars_file_name(filelist[j])
                    f_list.append([f, force, phase, h, k, l])
        return sorted(f_list)

    @staticmethod
    def pars_dirname(name):
        # splits = re.split(r'_', name)
        # print material, a, force
        pattern = re.compile(r'(\d*_?\d+kN)')
        pattern2 = re.compile(r'(\d*_?\d+)')
        pattern3 = re.compile(r'(\d+_?\d+)')
        force = 0
        for i in re.findall(pattern, name):
            for j in re.findall(pattern2, i):
                print "J: ", j
                if re.match(pattern3, j) is not None:
                    a, b = re.split('_', str(j))
                    # j = '{}.{}'.format(a, b)
                match = re.search(r"(\d*)(_)(\d+)", j)
                print match
                m = match.groups()
                if m[0] == '':
                    force = float(m[-1])
                else:
                    force = float(m[0] + '.' + m[-1])
                # force = float(j)
                print "Force: ", force
                # force = i
                # print "Force", force
        return force

    @staticmethod
    def pars_file_name(name):
        pattern_hkl = re.compile(r'(-?\d_-?\d_-?\d)')
        hkl = re.findall(pattern_hkl, name)
        ls = []
        # print name
        for i in hkl:
            # print i
            for j in re.findall(r'-?\d', str(i)):
                # print "hkl val: ", j
                ls.append(int(j))

        # print ls
        h, k, l = ls
        pattern_name = re.compile(r'([a-zA-Z_]+)(-?\d_-?\d_-?\d)')
        phase = ''
        pattern_phase = re.compile(r'[a-zA-Z]+_[a-zA-Z]+')
        for n, hk in re.findall(pattern_name, name):
            phase = n
        print phase
        for i in re.findall(pattern_phase, phase):
            print "Compiled: ", i
            phase = i
        return phase, h, k, l

    def load_data(self):
        f_list = self.get_all_files()
        dict = {}

        for i in f_list:
            if i[2] not in dict.keys():
                dict[i[2]] = {}

        for i in f_list:
            phase = i[2]
            force = i[1]
            if force not in dict[phase].keys():
                dict[phase][force] = []

        for i in xrange(len(f_list)):
            data_file = f_list[i][0]
            force = f_list[i][1]
            phase = f_list[i][2]
            h = f_list[i][3]
            k = f_list[i][4]
            l = f_list[i][5]
            file_content = open(data_file)
            lines = file_content.readlines()
            run_list = []
            for line in lines:
                if "#" in line:
                    pass
                else:
                    line = line.strip()  # removes withspaces at the frond and the end
                    line_content = re.split(r'\s*', line)
                    # print line_content
                    run, q, dq, d, dd, fwhm, dfwhm, i, di = line_content
                    run_list.append([run, d, dd])
                    # dict[phase][force].append
            step = 90 / (len(run_list) - 1)
            chi_list = np.arange(0, 90 + step, step)
            for j in xrange(len(run_list)):
                run = run_list[j][0]
                d = run_list[j][1]
                dd = run_list[j][2]
                chi = chi_list[j]
                dict[phase][force].append([chi, h, k, l, d, dd])
                print phase, force, chi, h, k, l, d, dd
        self.create_data_container(dict)

    def create_data_container(self, dict):
        phase_key = dict.keys()
        for i in xrange(len(phase_key)):  # loop over all phases
            phase = phase_key[i]
            self.Data.data_dict[phase] = {}
            force_key = sorted(dict[phase].keys())
            for j in xrange(len(force_key)):
                force = force_key[j]
                self.Data.data_dict[phase][force] = [[], []]
                if force != 0:
                    for k in xrange(len(dict[phase][force])):
                        # print "phase: ", phase, "Key: ", dict[phase].keys()
                        try:
                            chi_0, h_0, k_0, l_0, d_0, dd_0 = dict[phase][0][k]
                        except IndexError:
                            break
                        # print "unstraind: \t", chi_0, h_0, k_0, l_0, d_0, dd_0
                        inkrement = 0
                        while True:
                            chi, h, k, l, d, dd = dict[phase][force][inkrement]


                            if chi == chi_0 and h == h_0 and k == k_0 and l == l_0:
                                psi = chi
                                phi = 180
                                strain = None
                                strainerr = None
                                d_0 = float(d_0)
                                dd_0 = float(dd_0)
                                d = float(d)
                                dd = float(dd)
                                if d_0 > np.power(10., -10) and d > np.power(10., -10):

                                    strain = (d - d_0) / d_0
                                    strainerr = dd / d_0 + (d * dd_0) / (d_0 ** 2)
                                    stress, stresserr = self.calc_applied_stress(force)
                                    # if h == 2 and k == 2 and l == 2:
                                    #     print "straind: \t", force, chi, h, k, l, d, dd
                                    #     print strain, '\n'
                                    self.Data.data_dict[phase][force][0].append(
                                        [float(phi), float(psi), int(h), int(k), int(l)])
                                    self.Data.data_dict[phase][force][1].append([strain, strainerr, stress, stresserr])
                                break
                            inkrement += 1

    def calc_applied_stress(self, force):
        """
        :param force: applied force in kN
        :return: stress
        """
        area = (self.sample_diameter * np.power(10., -3.)) ** 2 / 4 * np.pi
        stress = force * np.power(10., 3) / area
        stress_error = stress * (2 * 0.01 / self.sample_diameter + 0.05)
        return stress, stress_error


class LoadSPODIData(DataRead):
    def __init__(self, diameter):
        super(LoadSPODIData, self).__init__(diameter)
        pass


class DataContainer(object):
    def __init__(self):
        self.data_dict = {}  # dictionary of the data. Key is the phase. val is the force dictionary. This has the force
        # as key and the list [phi_psi_hkl, strain_stress_list] as val's.

    def get_data_phase_1_force(self, force):
        return self.data_dict[1][force]

    def get_data_phase_2_force(self, force):
        return self.data_dict[2][force]

    def get_force_dict_phase_1(self):
        return self.data_dict[1]

    def get_force_dict_phase_2(self):
        return self.data_dict[2]
