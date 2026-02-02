# 📊 Exploratory Data Analysis – Key Insights (SCRUM-98)

## Dataset Overview
The dataset consists of **1,000 cleaned Spotify tracks** enriched with numerical audio features, including tempo, valence, energy, danceability, loudness, acousticness, and speechiness.  
All records passed validation checks, contained no critical missing values, and were suitable for exploratory analysis and downstream modeling.

---

## Feature Distributions
- **Valence, energy, and danceability** exhibit near-normal distributions with mild skewness, indicating balanced variability across tracks  
- **Tempo** is heavily concentrated within the medium BPM range, reflecting mainstream listening preferences  
- **Loudness** shows a relatively narrow range, consistent with modern audio mastering and compression practices  
- Acoustic and instrumental features show higher variance, suggesting stylistic diversity across tracks

---

## Correlation Analysis
Key relationships observed between audio features:
- **Energy and loudness** show a strong positive correlation, indicating louder tracks tend to be more energetic  
- **Danceability and valence** exhibit moderate correlation, suggesting happier tracks are more rhythmically suitable for dancing  
- **Acousticness and energy** display low correlation, highlighting a clear distinction between acoustic and high-energy music styles  

These correlations validate the use of valence, energy, and tempo as core features for mood and recommendation modeling.

---

## Mood Quadrant Insights (Valence × Energy)
Tracks were segmented into four mood quadrants using valence (positivity) and energy (intensity):

- **Happy & Energetic** and **Sad & Energetic** quadrants contain the majority of tracks  
- Calm tracks (low energy) are less frequent, indicating that higher-energy music dominates popular playlists  
- Mood segmentation provides a strong foundation for emotion-based filtering and recommendations  

This structure supports intuitive user interactions such as selecting songs by emotional state.

---

## Tempo Category Insights (SCRUM-95)
Tempo-based categories were created using BPM thresholds:

- **Slow (< 90 BPM)**: 5.4%  
- **Medium (90–130 BPM)**: 70.2%  
- **Fast (≥ 130 BPM)**: 24.4%  

The dominance of medium-tempo tracks confirms alignment with commercial radio and streaming trends, while fast-tempo tracks represent a significant high-energy segment.

---

## Key Takeaways
- **Energy and tempo** are defining characteristics of popular music  
- **Mood quadrants and tempo categories** provide complementary segmentation strategies  
- The dataset is well-balanced and structured for clustering, similarity analysis, and recommendation systems  
- Derived features improve interpretability without altering original data integrity  

---

## Next Steps
- Apply clustering algorithms (e.g., K-Means) using energy, valence, and tempo  
- Integrate mood and tempo filters into the CLI recommendation interface  
- Extend analysis to similarity-based recommendation methods (KNN, cosine similarity)  

---

**Status:** ✅ SCRUM-98 COMPLETE  
