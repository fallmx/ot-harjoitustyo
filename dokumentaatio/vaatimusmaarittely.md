# Vaatimusmäärittely

## Sovelluksen tarkoitus

Sovelluksella voi soittaa äänitiedostoja, kuten säestysraitoja, ja lisätä tiettyihin ajankohtiin merkkejä, joissa toisto pysähtyy odottamaan signaalia käyttäjältä. Tällöin säestysraita, jossa on välillä hiljaisuuksia, voidaan tahdistaa aloittamaan soittamisen uudelleen käyttäjän toimesta, kun käyttäjä on esimerkiksi soittanut soolo-osuutensa loppuun.

## Toiminnallisuudet

- Käyttäjä voi tuoda äänitiedoston ohjelmaan
- Käyttäjä voi soittaa äänitiedostoa
- Käyttäjä voi asettaa merkkejä eri ajankohtiin äänitiedostossa
- Toisto pysähtyy merkkeihin
- Jos käyttäjä painaa nappia, äänentoisto hyppää seuraavaan merkkiin
- Äänitiedostoon lisätyt merkit voidaan tallentaa/ladata projektitiedostosta

## Jatkokehitysideoita

- Käyttäjä voi määritellä haluamansa näppäimistö/MIDI-syötteen jatkamaan toistoa
- Lisää merkkityyppejä
    - Magneettinen merkki: määrätyn alueen sisällä tällaisesta merkistä äänentoisto voi hypätä taaksepäinkin siihen merkkiin. Täten toistoa voi tahdistaa, jos säestysraita ei ole kovin kuuluva siinä kohdassa pysyäkseen muuten tahdissa.
- Äänen aaltovisualisointi
    - Helpottaa havaitsemaan hiljaisuudet äänitiedostosta
