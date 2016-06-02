import load_data


class main(object):
    def __init__(self):
        print "Started program to create a the input file for the elastic constant calculator"
        self.select_inst()

    def select_inst(self):
        while True:
            print "Select Instrument:\n" \
                  "  -->(P)OLDI\n" \
                  "  -->(S)PODI (not implemented)\n" \
                  "  -->(E)xit"

            instrument = raw_input()
            if instrument == "P" or instrument == "p":
                print "insert samplediameter in mm:"
                dim = raw_input()
                self.load_data_object = load_data.LoadPOLDIData(diameter=dim)
                self.save_data_to_file()

            elif instrument == "S" or instrument == "s":
                print "insert samplediameter in mm:"
                dim = raw_input()
                self.load_data_object = load_data.LoadPOLDIData(dim)
                self.save_data_to_file()

            elif instrument == "E" or instrument == "e":
                self.exit()

            else:
                print "insert valid letter or exit with e"
                self.select_inst()

    def save_data_to_file(self):
        """
        save the data to a file laying in the same directory as this application
        :return:
        """

        print "finished reading data\n" \
              "write data to file \n" \
              "insert filename: \n"
        filename = raw_input()
        print "insert name of the material:"
        material = raw_input()
        self.load_data_object.save_data(filename, material)
        self.select_inst()


    def exit(self):
        quit()


if __name__ == "__main__":
    main()
