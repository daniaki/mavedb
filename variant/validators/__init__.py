from io import StringIO

import numpy as np
import pandas as pd
from django.core.exceptions import ValidationError

from core.utilities import is_null, null_values_list, format_column
from dataset.constants import (
    hgvs_pro_column,
    hgvs_nt_column,
    hgvs_columns,
    score_columns,
    variant_score_data,
    count_columns,
    variant_count_data,
    required_score_column,
    hgvs_tx_column,
)
from dataset.validators import (
    read_header_from_io,
    validate_at_least_one_additional_column,
    validate_has_hgvs_in_header,
    validate_header_contains_no_null_columns,
)
from .hgvs import (
    validate_multi_variant,
    validate_single_variant,
    validate_hgvs_string,
)
from .. import utilities

_EXTRA_NA_VALUES = set(
    list(null_values_list)
    + [str(x).lower() for x in null_values_list]
    + [str(x).upper() for x in null_values_list]
)


def validate_columns_match(variant, scoreset):
    """
    Validate that a child matches parents defined columns to keep
    data in sync.
    """
    try:
        if not variant.score_columns != scoreset.score_columns:
            raise ValidationError(
                f"Variant defines score columns '{variant.score_columns}' "
                f"but parent defines columns '{scoreset.score_columns}. "
            )
        if not variant.count_columns != scoreset.count_columns:
            raise ValidationError(
                f"Variant defines count columns '{variant.count_columns}' "
                f"but parent defines columns '{scoreset.count_columns}. "
            )
    except KeyError as error:
        raise ValidationError(error)


def validate_hgvs_nt_uniqueness(df):
    """Validate that hgvs columns only define a variant once."""
    dups = df.loc[:, hgvs_nt_column].duplicated(keep=False)
    if np.any(dups):
        dup_list = [
            "{} ({})".format(x, y)
            for x, y in zip(df.loc[dups, hgvs_nt_column], dups.index[dups])
        ]
        raise ValidationError(
            "duplicate HGVS nucleotide strings found: {}".format(
                ", ".join(sorted(dup_list))
            )
        )


def validate_hgvs_tx_uniqueness(df):
    """Validate that hgvs columns only define a variant once."""
    dups = df.loc[:, hgvs_tx_column].duplicated(keep=False)
    if np.any(dups):
        dup_list = [
            "{} ({})".format(x, y)
            for x, y in zip(df.loc[dups, hgvs_tx_column], dups.index[dups])
        ]
        raise ValidationError(
            "duplicate HGVS nucleotide strings found: {}".format(
                ", ".join(sorted(dup_list))
            )
        )


def validate_hgvs_pro_uniqueness(df):
    """Validate that hgvs columns only define a variant once."""
    dups = df.loc[:, hgvs_pro_column].duplicated(keep=False)
    if np.any(dups):
        dup_list = [
            "{} ({})".format(x, y)
            for x, y in zip(df.loc[dups, hgvs_pro_column], dups.index[dups])
        ]
        raise ValidationError(
            "Duplicate HGVS protein strings found: {}".format(
                ", ".join(sorted(dup_list))
            )
        )


def validate_scoreset_columns_match_variant(dataset_columns, variant_data):
    if sorted(dataset_columns[score_columns]) != sorted(
        list(variant_data[variant_score_data].keys())
    ):
        raise ValidationError(
            "Variant score columns do not match parent's columns."
        )
    if sorted(dataset_columns[count_columns]) != sorted(
        list(variant_data[variant_count_data].keys())
    ):
        raise ValidationError(
            "Variant count columns do not match parent's columns."
        )


def validate_variant_json(dict_):
    """
    Checks a given dictionary to ensure that it is suitable to be used
    as the `data` attribute in a :class:`Variant` instance.

    Parameters
    ----------
    dict_ : dict
        Dictionary of keys mapping to a list.
    """
    expected_keys = [variant_score_data, variant_count_data]
    for key in expected_keys:
        if key not in dict_.keys():
            raise ValidationError(
                "Missing the required key '%(key)'.",
                params={"data": dict_, "key": key},
            )

    if required_score_column not in dict_[variant_score_data]:
        raise ValidationError(
            "Missing required column '%(col)s' in variant's score data.",
            params={"col": required_score_column},
        )

    extras = [k for k in dict_.keys() if k not in set(expected_keys)]
    if len(extras) > 0:
        extras = [k for k in dict_.keys() if k not in expected_keys]
        raise ValidationError(
            "Encountered unexpected keys '%(extras)s'.",
            params={"extras": extras},
        )

    # Check the correct data types are given.
    for key in expected_keys:
        if not isinstance(dict_[key], dict):
            type_ = type(dict_[key]).__name__
            raise ValidationError(
                "Value for '%(key)' must be a dict not %(type)s.",
                params={"key": key, "type": type_},
            )


def validate_columns_are_numeric(df):
    """Checks non-hgvs columns for float or int data."""
    for column in df.columns:
        if column in hgvs_columns:
            continue
        else:
            if not (
                np.issubdtype(df.dtypes[column], np.floating)
                or np.issubdtype(df.dtypes[column], np.integer)
            ):
                raise ValidationError(
                    "Expected only float or int data columns. Got {}.".format(
                        str(df.dtypes[column])
                    )
                )


def validate_variant_rows(file):
    """
    Variant data validator that checks the following:

        1) Data types of rows must be either int, float or NoneType
        2) HGVS string is a valid hgvs string,
        3) Hgvs does not appear more than once in rows
        4) Validate hgvs_tx is present with hgvs_nt
        5) Validate g. prefix in hgvs_nt is accompanied by n./c. in hgvs_tx

    Variant strings must be `double-quoted` to ignore splitting multi-mutants
    on commas.

    Parameters
    ----------
    file : `io.FileIO` or `io.BytesIO` or `io.StringIO`
        An open file handle in read mode.

    Returns
    -------
    tuple[`List`, `Str`, `pd.DataFrame`]
        List of parsed header columns, and a dictionary mapping a hgvs string
        to a dictionary of column value pairs.
    """
    from ..models import column_order

    # Read header, validate and iterate one line since `read_header_from_io`
    # seeks back to the start.
    header = read_header_from_io(file)
    validate_has_hgvs_in_header(header)
    validate_at_least_one_additional_column(header)
    validate_header_contains_no_null_columns(header)

    # Convert django InMem/Tmp files into a StringIO for pandas.
    compat_io = StringIO()
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    compat_io.write(content)
    file = compat_io
    file.seek(0)

    # Load file in a dataframe for quicker processing.
    df = pd.read_csv(
        file,
        sep=",",
        encoding="utf-8",
        quotechar='"',
        names=header,
        skiprows=1,
        na_values=_EXTRA_NA_VALUES,
        keep_default_na=True,
    )
    df.rename(columns=lambda x: x.strip(), inplace=True)
    if not len(df):
        raise ValidationError(
            "No variants could be parsed from your input file. Please upload "
            "a non-empty file."
        )

    # Formats the data in each column replacing null values with np.NaN
    for column in df.columns:
        try:
            if column in hgvs_columns:
                df[column] = df[column].astype(str).map(str.strip)
                df[column] = format_column(df[column], astype=str)
            else:
                df[column] = format_column(df[column], astype=float)
        except ValueError as e:
            raise ValidationError(str(e).capitalize())

    # Determine which is the primary hgvs column. Defaults to _nt. _pro is only
    # selected when _nt is not provided.
    defines_nt_hgvs = hgvs_nt_column in df.columns
    defines_tx_hgvs = hgvs_tx_column in df.columns
    defines_p_hgvs = hgvs_pro_column in df.columns

    if defines_nt_hgvs:
        prefixes = {
            str(x).split(".")[0].lower() for x in df[hgvs_nt_column].values
        }

        if ("c" in prefixes or "n" in prefixes) and "g" in prefixes:
            raise ValidationError(
                "Genomic variants (prefix 'g.') cannot be mixed with "
                "transcript variants (prefix 'c.' or 'n.')."
            )

        if prefixes == {"g"} and not defines_tx_hgvs:
            raise ValidationError(
                "Transcript variants ('hgvs_tx' column) are required when "
                "specifying genomic variants (prefix 'g.' in the 'hgvs_nt' "
                "column)."
            )

    if defines_tx_hgvs and not defines_nt_hgvs:
        raise ValidationError(
            "Genomic variants ('hgvs_nt' column) must be defined when "
            "specifying transcript variants ('hgvs_tx' column)."
        )

    if defines_nt_hgvs and defines_p_hgvs:
        primary_hgvs_column = hgvs_nt_column
    elif defines_p_hgvs and not defines_nt_hgvs:
        primary_hgvs_column = hgvs_pro_column
    else:
        primary_hgvs_column = hgvs_nt_column

    # Apply variant formatting. Replace null type with None and strip.
    if defines_nt_hgvs:
        df[hgvs_nt_column] = df.loc[:, hgvs_nt_column].apply(
            utilities.format_variant, normalize=False
        )
    if defines_p_hgvs:
        df[hgvs_pro_column] = df.loc[:, hgvs_pro_column].apply(
            utilities.format_variant, normalize=False
        )
    if defines_tx_hgvs:
        df[hgvs_tx_column] = df.loc[:, hgvs_tx_column].apply(
            utilities.format_variant, normalize=False
        )

    # Check that the primary column is fully specified.
    null_primary = df.loc[:, primary_hgvs_column].apply(is_null)
    if any(null_primary):
        raise ValidationError(
            "Primary column (inferred as '{}') cannot "
            "contain any null values from '{}' (case-insensitive).".format(
                primary_hgvs_column, ", ".join(null_values_list)
            )
        )

    # Check that the hgvs_nt column does not have duplicate rows.
    if primary_hgvs_column == hgvs_nt_column:
        validate_hgvs_nt_uniqueness(df)

    # Validate variants where applicable
    if defines_nt_hgvs:
        df.loc[:, hgvs_nt_column].apply(
            validate_hgvs_string, column="nt", tx_present=defines_tx_hgvs
        )
    if defines_tx_hgvs:
        df.loc[:, hgvs_tx_column].apply(validate_hgvs_string, column="tx")
    if defines_p_hgvs:
        df.loc[:, hgvs_pro_column].apply(validate_hgvs_string, column="p")

    # Finally validate all other columns are numeric.
    validate_columns_are_numeric(df)

    # Sort header and remove hgvs cols since the hgvs strings are the map keys.
    if hgvs_nt_column not in df.columns:
        df[hgvs_nt_column] = None
    if hgvs_pro_column not in df.columns:
        df[hgvs_pro_column] = None
    if hgvs_tx_column not in df.columns:
        df[hgvs_tx_column] = None

    sorted_columns = [v for v in df.columns if v in hgvs_columns]
    sorted_columns += list(
        sorted(
            [v for v in df.columns if v not in hgvs_columns],
            key=lambda x: column_order[x],
        )
    )
    df = df[sorted_columns]
    df.index = pd.Index(df[primary_hgvs_column])

    # Convert np.NaN values to None for consistency across all columns and
    # for compatibility in PostgresSQL queries
    df = df.where((pd.notnull(df)), None)

    # Remove hgvs columns from header. Form validator expects only
    # additional non-hgvs in the returned header.
    non_hgvs_columns = [v for v in df.columns if v not in hgvs_columns]
    return non_hgvs_columns, primary_hgvs_column, df
