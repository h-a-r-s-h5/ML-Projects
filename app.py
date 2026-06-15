import pickle
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import gdown
import os

# -----------------------------
# Retry Session
# -----------------------------

session = requests.Session()

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)

# -----------------------------
# Poster Fetcher
# -----------------------------

@st.cache_data
def fetch_poster(movie_id):

    url = (
        f"https://api.themoviedb.org/3/movie/"
        f"{movie_id}"
        f"?api_key=b294949f303cb37354e19d1374e0a071"
        f"&language=en-US"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = session.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            return (
                "https://via.placeholder.com/"
                "300x450?text=No+Poster"
            )

        data = response.json()

        poster_path = data.get("poster_path")

        if not poster_path:
            return (
                "https://via.placeholder.com/"
                "300x450?text=No+Poster"
            )

        return (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    except Exception:
        return (
            "https://via.placeholder.com/"
            "300x450?text=No+Poster"
        )

# -----------------------------
# Recommendation Function
# -----------------------------

def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]
    top_similarity = movie_list[0][1]

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_match = []

    for i in movie_list:
        match = int((i[1] / top_similarity) * 100)
        recommended_match.append(min(match, 99))
        movie_id = movies.iloc[i[0]].movie_id

        recommended_movie_names.append(
            movies.iloc[i[0]].title
        )

        recommended_movie_posters.append(
            fetch_poster(movie_id)
        )

        recommended_match.append(match)

    return (
        recommended_movie_names,
        recommended_movie_posters,
        recommended_match
    )

# -----------------------------
# UI
# -----------------------------

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state = "collapsed"
)
st.markdown("""
<style>

.stApp{
    background-color:#0E1117;
}

h1,h2,h3{
    color:white;
}

div[data-testid="stSelectbox"] label{
    color:white;
    font-size:20px;
    font-weight:bold;
}

.movie-card{
    background-color:#1b1f24;
    padding:12px;
    border-radius:15px;
    transition:0.3s;
    text-align:center;
}

.movie-card:hover{
    transform:scale(1.03);
    box-shadow:0px 0px 20px rgba(255,255,255,0.15);
}

.movie-title{
    color:white;
    font-size:18px;
    font-weight:bold;
    margin-top:10px;
}

.movie-info{
    color:#bbbbbb;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

st.title("🎬 CineMatch AI")

movies = pickle.load(
    open("movie_list.pkl", "rb")
)

# Downloads similarity.pkl from Google Drive if not already present
if not os.path.exists("similarity.pkl"):
    gdown.download(
        "https://drive.google.com/uc?id=1mOYch_ElVjNK3asfpaj0pNhnjN99n3y_",
        "similarity.pkl",
        quiet=False
    )

similarity = pickle.load(open("similarity.pkl", "rb"))

movie_list = movies["title"].values

selected_movie = st.selectbox(
    "Discover your next favourite movie",
    movie_list
)

if st.button(
    " Recommend Movies",
    use_container_width=True
):

    with st.spinner("Finding similar movies..."):

        names, posters, matches = recommend(selected_movie)

    st.markdown("---")
    st.subheader(" Top Recommendations For You")

    cols = st.columns(5)

    for idx, col in enumerate(cols):

        with col:

            st.markdown(
                """
                <div class="movie-card">
                """,
                unsafe_allow_html=True
            )

            st.image(
                posters[idx],
                use_container_width=True
            )

            st.markdown(
                f"""
                <div class="movie-title">
                {names[idx]}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="movie-info">
                 {matches[idx]}% Match
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )