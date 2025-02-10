import argparse
import pandas as pd
import os
from helpers import tprint
from dev_test.part_msi_plot.diy_visualmsi.mysele.get_rc_distribution_baseline import (
    KmerRepeatCounter,
    MSILocusLoader,
    normalize_dataframe,
)
from msi_plot import msiplot


def generate_config(args):
    """
    Use arguments from the command line parameters (input: args)
    to generate a config setting dict.
    """
    config = {}

    config["genome"] = os.path.abspath(args.genome)
    if not os.path.isfile(config["genome"]):
        tprint("Error: {0} does not exist!".format(config["genome"]))
        exit(1)

    config["threads"] = int(args.threads)
    if config["threads"] < 1:
        tprint(
            "Error: Cannot specify less than one thread. "
            + "(Provided {0}).".format(config["threads"])
        )
        exit(1)

    config["bedfile"] = os.path.abspath(args.bedfile)
    if args.bedfile is None:
        tprint("Error: BED file not provided!")
        exit(1)
    else:
        bedfile = os.path.abspath(args.bedfile)
        if not os.path.isfile(bedfile):
            tprint("Error: {0} does not exist!".format(bedfile))
            exit(1)

    # normal and baseline file check
    if args.normal is None and args.baseline is None:
        tprint("tumor file only , only plot tumor bam")
    if args.normal is not None and args.baseline is not None:
        tprint("Error: Cannot provide both normal and baseline files!")
        exit(1)
    if args.normal is not None:
        config["normal_filepath"] = os.path.abspath(args.normal)
    if args.baseline is not None:
        config["baseline_filepath"] = os.path.abspath(args.baseline)

    if args.tumor is None:
        tprint("Error: Tumor BAM/SAM file not provided!")
        exit(1)
    else:
        config["tumor_filepath"] = os.path.abspath(args.tumor)

    if args.output is None:
        tprint("Error: Output filepath must be specified!")
        exit(1)
    elif not args.output.endswith(".png"):  # 以png结尾
        tprint("Error: Output filepath must end with.png!")
        exit(1)
    else:

        config["output_png_path"] = os.path.abspath(args.output)
        filename = os.path.basename(config["output_png_path"]).replace(".png", "")
        # Make sure output folder exists
        output_dir = os.path.dirname(config["output_png_path"])
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        config["output_tumor_path"] = os.path.join(
            output_dir, "{}.tumor.tsv".format(filename)
        )
        config["output_normal_path"] = os.path.join(
            output_dir, "{}.normal.tsv".format(filename)
        )

    config["min_read_quality"] = float(args.mrq)
    config["min_read_length"] = int(args.mrl)
    config["min_locus_quality"] = float(args.mlq)
    config["max_repeat_nums"] = int(args.mrn)
    config["debug_output"] = args.debug_output
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-n",
        "--normal",
        dest="normal",
        type=str,
        help="Normal input (SAM/BAM) file",
    )

    parser.add_argument(
        "-bsl",
        "--baseline",
        dest="baseline",
        type=str,
        help="Input tsv file for baseline.",
    )

    parser.add_argument(
        "-t",
        "--tumor",
        dest="tumor",
        required=True,
        type=str,
        help="Tumor input (SAM/BAM) file.",
    )

    parser.add_argument(
        "-b",
        "--bedfile",
        dest="bedfile",
        type=str,
        required=True,
        help="Input BED file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=True,
        type=str,
        help="png, compare normal and tumor",
    )

    parser.add_argument(
        "-mrq",
        "--min-read-quality",
        dest="mrq",
        type=float,
        default=10.0,
        help="Minimum average read quality.",
    )

    parser.add_argument(
        "-mlq",
        "--min-locus-quality",
        dest="mlq",
        type=float,
        default=20.0,
        help="Minimum average locus quality.",
    )

    parser.add_argument(
        "-mrl",
        "--min-read-length",
        dest="mrl",
        type=int,
        default=35,
        help="Minimum (unclipped/unmasked) read length.",
    )
    parser.add_argument(
        "--max_repeat_nums",
        dest="mrn",
        type=int,
        default=60,
        help="max repeat nums",
    )

    parser.add_argument(
        "--threads",
        dest="threads",
        type=int,
        default=1,
        help="Number of threads/proceseses to use.",
    )

    parser.add_argument(
        "--genome",
        dest="genome",
        required=True,
        type=str,
        help="Path to reference genome (FASTA).",
    )

    parser.add_argument(
        "--debug",
        dest="debug_output",
        action="store_true",
        help="Print debug output from multithreading.",
    )

    args = parser.parse_args()

    config = generate_config(args)
    tprint(
        "Processing normal input files with "
        + "{0} thread(s) ...".format(config["threads"])
    )
    krc = KmerRepeatCounter(config)
    mll = MSILocusLoader(config)
    msi_loci = mll.load_loci(config["bedfile"])
    tumor = krc.process(config["tumor_filepath"], msi_loci, config)
    tprint("Done processing tumor.")
    df = pd.DataFrame(tumor)
    df.sort_index(axis=0, inplace=True)
    df.fillna(0, inplace=True)
    df_fill = df.reindex(range(1, config["max_repeat_nums"] + 1), fill_value=0)
    df_fill = normalize_dataframe(df_fill)

    if "normal_filepath" in config:

        normal = krc.process(config["normal_filepath"], msi_loci, config)
        df_normal = pd.DataFrame(normal)
        df_normal.sort_index(axis=0, inplace=True)
        df_normal.fillna(0, inplace=True)
        df_normal_fill = df_normal.reindex(
            range(1, config["max_repeat_nums"] + 1), fill_value=0
        )
        df_normal_fill = normalize_dataframe(df_normal_fill)
        df_normal_fill.to_csv(config["output_normal_path"], sep="\t")
        tprint(
            "input normal file ,normal result saved in {}".format(
                config["output_normal_path"]
            )
        )
    elif "baseline_filepath" in config:
        tprint("input baseline file , reading...")
        df_normal_fill = pd.read_csv(config["baseline_filepath"], sep="\t", index_col=0)
    else:
        df_normal_fill = None
        tprint("input tumor file only , only plot tumor bam")

    df_fill.to_csv(config["output_tumor_path"], sep="\t")
    tprint("tumor tsv result saved in {}".format(config["output_tumor_path"]))

    msiplot(
        baseline=df_normal_fill, tumor=df_fill, output_file=config["output_png_path"]
    )
    tprint(
        "completed, the png file has been saved as {}".format(config["output_png_path"])
    )
