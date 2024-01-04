# IMPORT LIBRARY
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import time

# IMPORT DATASETS
url1 = 'https://github.com/Fery-K/MSDA_Gemini_1/raw/master/Datasets/Rekapitulasi_Gemini_1.xlsx'
url2 = 'https://github.com/Fery-K/MSDA_Gemini_1/raw/master/Datasets/Rekapitulasi_Gemini_2.xlsx'

penilaian1 = pd.read_excel(url1, engine='openpyxl', sheet_name='Penilaian')
kehadiran1 = pd.read_excel(url1, engine='openpyxl', sheet_name='Kehadiran')
kontribusi1 = pd.read_excel(url1, engine='openpyxl', sheet_name='Kontribusi')
auth1 = pd.read_excel(url1, engine='openpyxl', sheet_name='Authenticator')

penilaian2 = pd.read_excel(url2, engine='openpyxl', sheet_name='Penilaian')
kehadiran2 = pd.read_excel(url2, engine='openpyxl', sheet_name='Kehadiran')
kontribusi2 = pd.read_excel(url2, engine='openpyxl', sheet_name='Kontribusi')
auth2 = pd.read_excel(url2, engine='openpyxl', sheet_name='Authenticator')

# PAGE CONFIG
st.set_page_config(
    page_title='MSDA - Gemini',
    page_icon='♊',
    layout='wide',
    initial_sidebar_state='expanded')


# DEF FUNCTION
def stars(q, skor):
    star = 0
    if skor < q.iloc[0]:
        star = 1
    elif q.iloc[0] <= skor < q.iloc[1]:
        star = 2
    elif q.iloc[1] <= skor < q.iloc[2]:
        star = 3
    elif q.iloc[2] <= skor < q.iloc[3]:
        star = 4
    elif skor >= q.iloc[3]:
        star = 5

    return star


def verified(name, auth, penilaian, kehadiran, kontribusi):
    div = auth[auth['Nama'] == name]['Staff Divisi'].values[0]
    st.header('Laporan Performa Staff BPH UBT Bersinar ✨')
    col1, col2, col3 = st.columns([1, 1, 0.75])
    col1.subheader(f'Nama: {name}')
    col2.subheader(f'Staff Divisi: {div}')
    # st.divider()
    tab1, tab2 = st.tabs(['Overview', 'Report'])
    with tab1:
        col_a, col_b = st.columns([1, 1])
        with col_a:
            P1 = penilaian[penilaian['Nama'] == name]['Problem solving'].values[0] * 100 / 3
            P2 = penilaian[penilaian['Nama'] == name]['Communication skill'].values[0] * 100 / 3
            P3 = penilaian[penilaian['Nama'] == name]['Tepat waktu'].values[0] * 100 / 3
            P4 = penilaian[penilaian['Nama'] == name]['Responsif'].values[0] * 100 / 4
            P5 = penilaian[penilaian['Nama'] == name]['Atensi'].values[0] * 100 / 4
            P6 = penilaian[penilaian['Nama'] == name]['Kinerja Dalam Divisi'].values[0] * 100 / 5

            df_nilai = pd.DataFrame({'r': [P1, P2, P3, P4, P5, P6],
                                     'theta': ['Problem Solving', 'Communication Skill', 'Tepat Waktu',
                                               'Responsif', 'Atensi', 'Kinerja Dalam Divisi']})
            plot_nilai = px.line_polar(df_nilai, r='r', theta='theta', line_close=True)
            plot_nilai.update_traces(fill='toself')
            plot_nilai.update_polars(bgcolor='grey')
            plot_nilai.update_layout(dragmode=False)

            st.subheader('Penilaian Divisi')
            st.plotly_chart(plot_nilai, use_container_width=True)
        with col_b:
            panit = kontribusi.columns.values[2:-1]
            nilai_panit = kontribusi[kontribusi['Nama'] == name].loc[:, panit].values[0]
            n_ketupel, n_kabid, n_kadiv, n_staff, n_cp, n_absen = 0, 0, 0, 0, 0, 0
            for n in nilai_panit:
                if n == 3:
                    n_ketupel += 1
                elif n == 2.5:
                    n_kabid += 1
                elif n == 2:
                    n_kadiv += 1
                elif n == 1:
                    n_staff += 1
                elif n == 0.5:
                    n_cp += 1
                else:
                    n_absen += 1

            df_panit = pd.DataFrame({'Jabatan': ['Ketua Pelaksana / Ring 0', 'Ring 1',
                                                 'Ring 2 / Panit SyukWis Okt', 'CP OpRec MPAB', 'Staff', 'Absen'],
                                     'Total': [n_ketupel, n_kabid, n_kadiv, n_staff, n_cp, n_absen]})
            plot_panit = alt.Chart(df_panit, title='Partisipasi Dalam Kepanitiaan UBT').mark_arc(innerRadius=50).encode(
                alt.Theta('Total'),
                alt.Color('Jabatan:O', title='Kontribusi', sort=['Absen', 'Staff', 'Ketua Divisi / Ring 2',
                                                                 'Ketua Bidang / Ring 1', 'Ketua Pelaksana / Ring 0'])
            )
            st.subheader('Kepanitiaan')
            st.altair_chart(plot_panit, use_container_width=True)

        st.divider()

        col_c, col_d, col_e = st.columns([2.25, 1.5, 2])
        col_d.subheader('Kehadiran Dalam ProKer UBT')

        proker_all = kehadiran.columns.values[2:-1]
        proker_dist = []
        for i in range(len(proker_all)):
            proker_dist.append(proker_all[i].split(' - ', 1)[0])
        n_hadir = kehadiran[kehadiran['Nama'] == name].loc[:, proker_all].values[0]

        # Dataframe semua proker
        df_proker_all = pd.DataFrame({
            'Divisi': proker_dist,
            'Kehadiran': [1 for i in range(len(proker_dist))]
        })
        df_proker_all = df_proker_all.groupby('Divisi').agg({'Kehadiran': 'sum'}).reset_index()
        df_proker_all['Keterangan'] = ['Total' for i in range(df_proker_all.shape[0])]

        # Dataframe proker yang dihadiri
        df_proker_hadir = pd.DataFrame({
            'Divisi': proker_dist,
            'Kehadiran': n_hadir
        })
        df_proker_hadir = df_proker_hadir.groupby('Divisi').agg({'Kehadiran': 'sum'}).reset_index()
        df_proker_hadir['Keterangan'] = ['Hadir' for i in range(df_proker_hadir.shape[0])]

        # Dataframe gabungan
        df_hadir = pd.concat([df_proker_all, df_proker_hadir])
        df_hadir['Keterangan'] = df_hadir['Keterangan'].astype(pd.CategoricalDtype(['Total', 'Hadir'], ordered=True))

        plot_hadir = alt.Chart(df_hadir).mark_bar().encode(
            alt.X('Divisi', title='').axis(labelAngle=0),
            alt.Y('Kehadiran').axis(values=[i for i in range(0, df_hadir['Kehadiran'].max() + 1)], format='~s'),
            alt.Color('Keterangan', title='', sort=['Total', 'Hadir']),
            xOffset='Keterangan'
        ).configure_view(stroke=None)

        st.altair_chart(plot_hadir, use_container_width=True)

    with tab2:
        col1, col2 = st.columns([2, 2])
        st.divider()
        col3, col4 = st.columns([2, 2])
        st.divider()
        col5, col6 = st.columns([2, 2])
        st.divider()
        col7, col8 = st.columns([2, 2])
        st.divider()

        skor_nilai = penilaian[penilaian['Nama'] == name]['Skor Nilai'].values[0]
        skor_hadir = kehadiran[kehadiran['Nama'] == name]['Skor Kehadiran'].values[0]
        skor_kontribusi = kontribusi[kontribusi['Nama'] == name]['Skor Kontribusi'].values[0]
        skor_total = auth[auth['Nama'] == name]['Total'].values[0]

        q_nilai = penilaian['Skor Nilai'].quantile([.2, .4, .6, .8])
        q_nilai.iloc[1] = q_nilai.iloc[1]-1
        q_hadir = kehadiran['Skor Kehadiran'].quantile([.2, .4, .6, .8])
        q_kontribusi = kontribusi['Skor Kontribusi'].quantile([.2, .4, .6, .8])
        q_total = auth['Total'].quantile([.2, .4, .6, .8])

        emot = '⭐'
        with col1:
            st.subheader(f'Penilaian Divisi: {emot * stars(q_nilai, skor_nilai)}')
        with col3:
            st.subheader(f'Kepanitiaan: {emot * stars(q_hadir, skor_hadir)}')
        with col5:
            st.subheader(f'Kehadiran: {emot * stars(q_kontribusi, skor_kontribusi)}')
        with col7:
            st.subheader(f'Performa Keseluruhan: {emot * stars(q_total, skor_total)}')

        with col2:
            k_nilai = auth[auth['Nama'] == name]['Komentar Penilaian'].values[0]
            st.markdown(f'''
            {k_nilai}
            ''')
        with col4:
            k_kontribusi = auth[auth['Nama'] == name]['Komentar Kontribusi'].values[0]
            st.markdown(f'''
            {k_kontribusi}
            ''')
        with col6:
            k_hadir = auth[auth['Nama'] == name]['Komentar Kehadiran'].values[0]
            st.markdown(f'''
            {k_hadir}
            ''')
        with col8:
            k_all = auth[auth['Nama'] == name]['Komentar Total'].values[0]
            st.markdown(f'''
            {k_all}
            ''')

        st.header('')
        st.header('')
        col_a, col_b, col_c = st.columns([1, 2.5, 1])
        with col_a:
            st.markdown('**Ketua Umum BPH UBT ITB 2023/2024**')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.markdown('**Bintang Adra Sapardiman**')
        with col_c:
            st.markdown('**Ketua Divisi MSDA BPH UBT ITB 2023/2024**')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.markdown('**Fery Kurniawan**')


def unverified(name, auth):
    div = auth[auth['Nama'] == name]['Staff Divisi'].values[0]
    st.header('Laporan Performa Staff BPH UBT Bersinar ✨')
    col1, col2, col3 = st.columns([1, 1, 0.1])
    col1.subheader(f'Nama: {name}')
    col2.subheader(f'Staff Divisi: {div}')
    st.divider()

    col1, col2 = st.columns([0.4, 1])
    col2.subheader('Hayoloo.. ID Line nya ngga sesuai !')


def init(name, auth):
    div = auth[auth['Nama'] == name]['Staff Divisi'].values[0]
    st.header('Laporan Performa Staff BPH UBT Bersinar ✨')
    col1, col2, col3 = st.columns([1, 1, 0.1])
    col1.subheader(f'Nama: {name}')
    col2.subheader(f'Staff Divisi: {div}')
    st.divider()

    col1, col2 = st.columns([0.2, 1])
    col2.subheader('Masukkan ID Line yang terdaftar saat Pendataan Anggota')


# BODY
with st.sidebar:
    rekap = st.selectbox('', ['PERIODE #1', 'PERIODE #2'])

    iNama = st.selectbox('Pilih Nama Kalian', auth2['Nama'].tolist())
    iPass = st.text_input('Masukkan ID Line kalian', '--ID Line--')

    with st.spinner('Tunggu Bentar...'):
        time.sleep(2)

    st.divider()

    st.caption('Jika mempunyai pertanyaan atau mengalami kendala, langsung contact staff MSDA yang ada di divisi kalian,'
               ' gas ngengg...')

verif = auth2[auth2['Nama'] == iNama]['ID Line'].values[0]

if iPass == verif:
    if rekap == 'PERIODE #1':
        verified(iNama, auth1, penilaian1, kehadiran1, kontribusi1)
    else:
        verified(iNama, auth2, penilaian2, kehadiran2, kontribusi2)
elif iPass == '--ID Line--':
    init(iNama, auth2)
else:
    if rekap == 'PERIODE #1':
        unverified(iNama, auth1)
    else:
        unverified(iNama, auth2)
