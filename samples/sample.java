import javax.crypto.Cipher;
import java.security.Signature;

class Sample {
    void demo() throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        Signature signature = Signature.getInstance("SHA256withECDSA");
    }
}