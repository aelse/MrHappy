import sys

def parse_options():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config_file", metavar="FILE",
        help="bot configuration file")
    parser.add_option("-v", "--verbose", dest="verbose", default=False,
        help="print verbose status information")
    (options, args) = parser.parse_args()
    return options

def main():
    options = parse_options()
    return 0

if __name__ == "__main__":
    sys.exit(main())
