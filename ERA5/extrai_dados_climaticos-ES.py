import cdsapi
import sys

if len(sys.argv) < 2:
    print("ERRO: incluir o ano")
    sys.exit(1)

ano = sys.argv[1]

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        #'variable': '2m_temperature',

        'variable': [
            '2m_temperature',
            'total_precipitation',
            'surface_pressure',
            '2m_dewpoint_temperature',
            '10m_u_component_of_wind',
            '10m_v_component_of_wind'
        ],


        'year': f"{ano}",
        'month': [
            '01','02','03','04','05','06',
            '07','08','09','10','11','12'
        ],
        'time': '00:00',
        'format': 'netcdf',
        'area': [
            -18.0,  # Norte
            -42.0,  # Oeste
            -21.5,  # Sul
            -39.0,  # Leste
        ],
    },
    f"dados-climaticos/{ano}/temp_era5_{ano}_es.nc"
)

print(f"Download finalizado para o ano {ano}!")

