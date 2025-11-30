import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io
import os
# AI Library (rembg) - Streamlit માં અલગથી ઇન્સ્ટોલ કરવું પડશે
try:
    from rembg import remove
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# --- મુખ્ય વેબ એપ ફંક્શન ---
def main():
    st.set_page_config(
        page_title="AI Photo Lab - Web Editor",
        layout="wide"
    )
    
    # હેડર
    st.title("📸 AI PHOTO LAB (Web Version)")
    st.markdown("---")
    
    # ફાઈલ અપલોડર
    uploaded_file = st.file_uploader("🖼️ ફોટો અપલોડ કરો", type=["jpg", "jpeg", "png"])

    # જો કોઈ ફાઇલ અપલોડ થયેલ હોય તો જ આગળ વધો
    if uploaded_file is not None:
        # ફોટો લોડ કરો
        original_image = Image.open(uploaded_file).convert("RGB")
        
        # --- ડાબી બાજુ: કંટ્રોલ પેનલ (સાઇડબારમાં) ---
        st.sidebar.header("⚙️ એડિટિંગ કંટ્રોલ")
        
        # બ્રાઇટનેસ સ્લાઇડર
        st.sidebar.markdown("### બ્રાઇટનેસ અને કોન્ટ્રાસ્ટ")
        brightness_val = st.sidebar.slider("બ્રાઇટનેસ", 0.1, 2.0, 1.0, 0.1)
        
        # કોન્ટ્રાસ્ટ સ્લાઇડર
        contrast_val = st.sidebar.slider("કોન્ટ્રાસ્ટ", 0.1, 2.0, 1.0, 0.1)
        
        # --- ફિલ્ટર્સ ---
        st.sidebar.markdown("### ફિલ્ટર્સ અને ઇફેક્ટ્સ")
        
        col1, col2 = st.sidebar.columns(2)
        
        # Filter Logic (B&W)
        if col1.button("⚫ B&W"):
            # Streamlit માં, આપણે State નો ઉપયોગ કરીને ઇમેજને અપડેટ કરીએ છીએ
            st.session_state['filter'] = 'bw'
        
        # Filter Logic (Sepia)
        if col2.button("🟤 Sepia"):
            st.session_state['filter'] = 'sepia'
            
        # AI/Reset Buttons
        st.sidebar.markdown("---")
        if st.sidebar.button("🤖 AI Background Remove"):
            if AI_AVAILABLE:
                # AI લોજિક માટે એક થ્રેડ શરૂ કરી શકાય છે અથવા અહીં સીધી લોજિક મૂકી શકાય છે
                st.info("AI દ્વારા બેકગ્રાઉન્ડ રિમૂવ થઈ રહ્યું છે...")
                st.session_state['filter'] = 'rembg'
            else:
                st.error("rembg લાઈબ્રેરી ઇન્સ્ટોલ નથી.")
        
        # --- એડિટિંગ લોજિક લાગુ કરો ---
        
        # Filter લાગુ કરો (જો કોઈ બટન દબાયું હોય)
        processed_image = original_image.copy()
        
        if 'filter' in st.session_state:
            if st.session_state['filter'] == 'bw':
                processed_image = processed_image.convert("L").convert("RGB")
            elif st.session_state['filter'] == 'sepia':
                gray = processed_image.convert("L")
                processed_image = ImageOps.colorize(gray, "#3e2723", "#fff3e0").convert("RGB")
            elif st.session_state['filter'] == 'rembg':
                # rembg લોજિક અહીં આવશે
                try:
                    processed_image = remove(processed_image) # output with alpha channel
                    st.success("✅ બેકગ્રાઉન્ડ સફળતાપૂર્વક રિમૂવ થયું!")
                except Exception as e:
                    st.error(f"AI ભૂલ: {e}")
                    
        # સ્લાઇડર લોજિક લાગુ કરો
        edited_image = ImageEnhance.Brightness(processed_image).enhance(brightness_val)
        edited_image = ImageEnhance.Contrast(edited_image).enhance(contrast_val)

        # --- જમણી બાજુ: ડિસ્પ્લે ---
        st.header("✨ એડિટ કરેલો ફોટો")
        st.image(edited_image, caption='તમારી વેબ એપમાં ફોટો', use_column_width=True)
        
        # ડાઉનલોડ બટન
        buf = io.BytesIO()
        edited_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 ફોટો ડાઉનલોડ કરો (PNG)",
            data=byte_im,
            file_name="edited_photo.png",
            mime="image/png"
        )
    else:
        # જો ફાઇલ અપલોડ ન હોય તો
        st.info("કૃપા કરીને ફોટો એડિટિંગ શરૂ કરવા માટે એક ફાઇલ અપલોડ કરો.")


if __name__ == "__main__":
    main()