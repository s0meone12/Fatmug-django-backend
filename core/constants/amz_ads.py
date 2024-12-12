from datetime import datetime

PRE_API_AMZ_ADS_VARS = {
    'fetch_performance_rpt_from_gdrive_till_date': datetime(2023, 11, 4).date(),
    'prefix': {
        'sp_st': 'SP_Search_Term_',
        'sp_tgt': 'SP_Targeting_',
        'sd_mt': 'SD_Matched_Target_',
        'sb_st': 'SB_Search_Term_',
    },
    'start_dates': {
        'sp_st': datetime(2022, 12, 31).date(),
        'sp_tgt': datetime(2022, 12, 13).date(),
        'sd_mt': datetime(2022, 11, 29).date(),
        'sb_st': datetime(2022, 12, 31).date(),
    },
    'pre_api_report_date_columns': {
        'sp_st': ['Date'],
        'sb_st': ['Date'],
        'sd_mt': ['Start Date', 'End Date'],
        'sp_tgt': ['Date'],
    },
}

AMZ_ADS_VARS = {
    'negative_targets': {
        'days_delay': 30,
    }
}
