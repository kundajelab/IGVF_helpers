import csv
from typing import Dict
import argparse
from pathlib import Path
import gzip


def make_pseudobulks(
    annotations_in: Path, cluster_col: str, fragments_in: Path, outpath: Path
) -> None:
    """Using a list of barcodes and clusters, create pseudobulks from reads from different samples

    Args:
        annotations_in: path to annotations.tsv file. Must have one col called cellBC_formatted with
        barcodes that can be matched to the ones in the IGVF fragments file (i.e. just ATGC;
        no prefixes/suffixes) and one col describing the cluster. This col will be passed as the
        "cluster_col" variable
        cluster_col: Name of col to be used as pseudobulk name (can be a cell type or numeric ID)
        fragments_in: Path to fragments file
        outpath: where to save pseudobulks
    """
    # make barcode dictionary
    barcodes_to_clusters: Dict = {}
    with annotations_in.open("r") as f_in:
        csv_reader = csv.DictReader(f_in, delimiter=",")
        for line in csv_reader:
            barcodes_to_clusters[line["cellBC_formatted"]] = line[cluster_col]

    # make outfiles for all clusters
    # get unique cluster IDs with set
    # barcodes_to_clusters.values() gives the cluster number -- this becomes the key for
    # clusters_to_outfiles
    clusters = set(barcodes_to_clusters.values())
    clusters_to_outfiles: Dict = {
        cluster: outpath / f"{cluster}.tsv" for cluster in clusters
    }

    # open all outfiles (use this approach because opening files all at once is faster
    # than opening/closing each of them for each barcode and also so that we can access all pseudobulk
    # files for all barcodes in fragments files)
    open_outfs: Dict = {
        key: value.open("a") for key, value in clusters_to_outfiles.items()
    }
    print(f"Created {open_outfs.keys()} files")

    # create set of barcodes to make matching to barcodes in file easier
    all_barcodes = set(barcodes_to_clusters.keys())
    barcode_counter = 0
    filtered_counter = 0
    with gzip.open(fragments_in, "r") as frag_in:
        for line_bytes in frag_in:
            line = line_bytes.decode()
            # check that line is split by '\t'; otherwise it might be a header
            if len(line.split("\t")) != 5:
                # print(f"Header line: {line}")
                continue
            chrom, start, end, barcode, num_frags = line.rstrip("\n").split("\t")
            if barcode not in all_barcodes:
                # print(f"Barcode filtered: {barcode}")
                filtered_counter += 1
                continue
            cluster_num = barcodes_to_clusters[barcode]
            # print(f"Wrote barcode {barcode}")
            barcode_counter += 1
            open_outfs[cluster_num].write(line)

    # close all the open files
    for open_outf in open_outfs.values():
        open_outf.close()

    print("Total barcodes sent to pseudobulks: {barcode_counter}")
    print("Total filtered barcodes: {filtered_counter}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create pseudobulks from fragment files and cell metadata"
    )
    parser.add_argument(
        "--annotations_in", type=Path, required=True, help="Path to cell_metadata.csv"
    )
    parser.add_argument(
        "--cluster_col",
        type=str,
        required=True,
        help="Col with cluster (e.g. cell type) info",
    )
    parser.add_argument(
        "--outpath", type=Path, required=True, help="Top dir for saving pseudobulks"
    )
    parser.add_argument(
        "--fragments_in", type=str, required=True, help="Path to fragments file"
    )

    args = parser.parse_args()

    make_pseudobulks(
        annotations_in=args.annotations_in,
        cluster_col=args.cluster_col,
        outpath=args.outpath,
        fragments_in=args.fragments_filename,
    )
