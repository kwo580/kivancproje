import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = "Çok gizli bir key"
uri = os.getenv('MONGO_ATLAS_URI')
client = MongoClient(uri)
hayvanlar = client.sahiplen.hayvanlar
uyeler = client.sahiplen.uyeler


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/sahiplendir')
def sahiplendir():
    return render_template('sahiplendir.html')


@app.route('/sahiplen')
def sahiplen():
    yapilacaklar = []
    for yap in hayvanlar.find():
          yapilacaklar.append({"_id": str(yap['_id']), "ad": yap['ad'],"soyad": yap['soyad'],"tur": yap['tur'], "adres": yap['adres'],"yorum": yap['yorum']}) 
    return render_template('sahiplen.html',veri=yapilacaklar)

@app.route('/giris',methods=['GET'])
def giris():
    return render_template('giris.html')
@app.route('/uye',methods=['GET', 'POST'])
def uye():
    return render_template('uyekayit.html')



@app.route('/girisyap',methods=['GET', 'POST'])
def girisyap():
    if request.method == 'POST':
        # index.html formundan isim gelecek
        mail = request.form["email"]
        parola = request.form["parola"]
        veritabani=uyeler.find_one({"mail": mail})
        # epostaya ait olan kullanıcı var
        if   veritabani is not  None :
          if parola == veritabani.get('parola'):
            # şifre de eşleşiyorsa giriş başarılıdır
            # kullanıcının epostasını session içine al
            session['ad'] =  veritabani.get('ad')
            session['soyad'] =  veritabani.get('soyad')
            session['adres'] =  veritabani.get('adres')
            session['mail']= mail
            # todo ekleyebileceği sayfaya yönlendiriyoruz.
            return redirect('/sahiplen')
          else:
            durum="Hatalı şifre girdiniz"
            return render_template('giris.html',hata=durum)
        else:
            durum="Hatalı email girdiniz"
            return render_template('giris.html',hata=durum)
    else:
        return render_template('sayfayok.html')


@app.route('/uyeol',methods=["POST"])
def uyeol():
  if request.method == 'POST':
        # index.html formundan isim gelecek
        ad = request.form["ad"]
        soyad = request.form["soyad"]
        mail = request.form["email"]
        adres = request.form["adres"]
        parola = request.form["parola"]
        session['ad'] = ad
        session['soyad'] =  soyad
        session['adres'] = adres
        session['mail']= mail
        mydict = { "ad": ad, "soyad":soyad, "mail": mail ,"adres": adres,"parola":parola}
        u = uyeler.find_one({'mail':mail})
        if u is None :
                x = uyeler.insert_one(mydict)
                return redirect('/sahiplendir')
        else:
            durum="email önceden eklenmiş"
            return render_template('uyekayit.html',hata=durum)

  return redirect('/')
@app.route('/sahiplendirkayit',methods=["POST"])
def sahiplendirkayit():
  if request.method == 'POST':
    try:
        # index.html formundan isim gelecek
        ad = session['ad']
        soyad = session['soyad']
        yorum = request.form["yorum"]
        adres = session['adres']
        tur = request.form["tur"]
       
        mydict = { "ad": ad, "soyad":soyad, "yorum": yorum ,"adres": adres,"tur":tur}
        hayvanlar.insert_one(mydict)
        return redirect('/sahiplen')
    except:
            durum="Giriş yapmadınız"
            return render_template('giris.html',hata=durum)
  return redirect('/')

@app.route('/cikisyap',methods=['GET', 'POST'])
def cikisyap():
    session.pop('ad', None)
    session.pop('soyad', None)
    session.pop('mail', None)
    session.pop('adres', None)
    return redirect('/')

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
 