import pickle
import streamlit as st
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_models():
    mov = pickle.load(open('movie_list.pkl', 'rb'))
    sim = pickle.load(open('similarity.pkl', 'rb'))
    return mov, sim

try:
    movies, similarity = load_models()
except FileNotFoundError as e:
    st.error("Model files not found: {}\nMake sure pkl files exist.".format(e))
    st.stop()


# ---------------- POSTER FUNCTION ----------------
def fetch_poster(movie_id):
    try:
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        return "https://via.placeholder.com/500x750?text=No+Image"

    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=Error"


# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie_name):
    try:
        index = movies[movies['title'] == movie_name].index[0]
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], []

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_titles = []
    recommended_posters = []

    for item in distances[1:6]:
        movie_id = movies.iloc[item[0]].movie_id
        recommended_titles.append(movies.iloc[item[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters


# ---------------- UI ----------------
st.title("🎬 Movie Recommender System")
st.markdown("Select a movie and get 5 similar recommendations!")

movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", sorted(movie_list))

if st.button("Recommend", type="primary"):
    names, posters = recommend(selected_movie)

    if names:
        st.subheader("Recommended Movies")
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_column_width=True)
                st.caption(names[i])



