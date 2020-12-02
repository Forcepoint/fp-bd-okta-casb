# Author:  Dlo Bagari
# created Date: 11-11-2019

from cli.cli_args import CliArgs

if __name__ == "__main__":
    cli_args = CliArgs("casb_risk_score.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    args.function(args)
