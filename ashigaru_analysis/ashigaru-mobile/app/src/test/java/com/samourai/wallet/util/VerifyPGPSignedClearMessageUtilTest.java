package com.samourai.wallet.util;

import static com.samourai.wallet.util.tech.VerifyPGPSignedClearMessageUtil.verifySignedMessage;

import static java.lang.String.format;

import org.junit.Assert;
import org.junit.Test;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.DecimalFormat;
import java.util.stream.Collectors;

public class VerifyPGPSignedClearMessageUtilTest {

    private static final String SIGNED_MESSAGE =
                    "-----BEGIN PGP SIGNED MESSAGE-----\n" +
                            "Hash: SHA512\n" +
                            "\n" +
                            "latest_ashigaru_mobile_version=v2.0.0\n" +
                            "\n" +
                            "latest_ashigaru_mobile_apk=ashigaru_mobile_v2.0.0.apk\n" +
                            "-----BEGIN PGP SIGNATURE-----\n" +
                            "\n" +
                            "iQIzBAEBCgAdFiEERF+AeZb3BYa3Fce4oTgGsfoqZ2sFAmbLYQcACgkQoTgGsfoq\n" +
                            "Z2s/Zw/9GPqC2rPDVZb0ZGZTDGm6NbcGd4DLTd9rJIxmpGz7Ge5kU6N7M1MEE0jV\n" +
                            "lBygcucQMP/G/9UCHUVK258ISU8VmRdGcDEUjys7Ge0LgEi5iRp+TK+HB1npFpNC\n" +
                            "suKcW2/+sVTUJYA2se1GxcwC8Gj4J0FWJqjoGRn6EDrUzr7tIDpt8pPdBISVRNAM\n" +
                            "sLKXtqQAVN/+zthyZgFilR/KDKir7EY4BoU8WCmluFLpwj6t93vxCh7gQ0+p+qZf\n" +
                            "xKPUNFvucIb9Nnj4NsGW4c/0Ej+LU/MJAwSmk7VbkpaOd9+yA12ONEd4Qw5ARFfF\n" +
                            "o4wDHeFg4TT0/uIwxURIMMlpKbDkuldLz6v7cPcQvnjYe6I8u5CPao9yXPLeaX8Y\n" +
                            "GVkJQje835mq43VisRac/FdbK1MvwrS6mZxnNOIWf4G/YCBZ9o/pI6dfMcpj/rv8\n" +
                            "VyJ+AKKGJS//Dcs4eRaybUsE7gf+dTlrHlnAJKQtkq82sl2DQRgc/7gw31Ih/l0i\n" +
                            "u531ALMnaK0hR5WLvmtx8jesvGA4NPAE/sHOemgH/gzp+VaEUrMhn7J6uC/wT8NQ\n" +
                            "HNUt1V6ikuTE932FLuX1XHXKuGpIqyQ2VmtOe1CSrsYCbzZGdT2eVecUcg+VDDpf\n" +
                            "T83WLkXyPbMVlQ0stPusT9oTP8GZEYBKQB6hkHFXYsKyd25TVx4=\n" +
                            "=M1Gb\n" +
                            "-----END PGP SIGNATURE-----\n";

    /* remove last character from the good signature 'SIGNED_MESSAGE' */
    private static final String BAD_SIGNED_MESSAGE =
            "-----BEGIN PGP SIGNED MESSAGE-----\n" +
                    "Hash: SHA512\n" +
                    "\n" +
                    "latest_ashigaru_mobile_version=v2.0.0\n" +
                    "\n" +
                    "latest_ashigaru_mobile_apk=ashigaru_mobile_v2.0.0.apk\n" +
                    "-----BEGIN PGP SIGNATURE-----\n" +
                    "\n" +
                    "iQIzBAEBCgAdFiEERF+AeZb3BYa3Fce4oTgGsfoqZ2sFAmbLYQcACgkQoTgGsfoq\n" +
                    "Z2s/Zw/9GPqC2rPDVZb0ZGZTDGm6NbcGd4DLTd9rJIxmpGz7Ge5kU6N7M1MEE0jV\n" +
                    "lBygcucQMP/G/9UCHUVK258ISU8VmRdGcDEUjys7Ge0LgEi5iRp+TK+HB1npFpNC\n" +
                    "suKcW2/+sVTUJYA2se1GxcwC8Gj4J0FWJqjoGRn6EDrUzr7tIDpt8pPdBISVRNAM\n" +
                    "sLKXtqQAVN/+zthyZgFilR/KDKir7EY4BoU8WCmluFLpwj6t93vxCh7gQ0+p+qZf\n" +
                    "xKPUNFvucIb9Nnj4NsGW4c/0Ej+LU/MJAwSmk7VbkpaOd9+yA12ONEd4Qw5ARFfF\n" +
                    "o4wDHeFg4TT0/uIwxURIMMlpKbDkuldLz6v7cPcQvnjYe6I8u5CPao9yXPLeaX8Y\n" +
                    "GVkJQje835mq43VisRac/FdbK1MvwrS6mZxnNOIWf4G/YCBZ9o/pI6dfMcpj/rv8\n" +
                    "VyJ+AKKGJS//Dcs4eRaybUsE7gf+dTlrHlnAJKQtkq82sl2DQRgc/7gw31Ih/l0i\n" +
                    "u531ALMnaK0hR5WLvmtx8jesvGA4NPAE/sHOemgH/gzp+VaEUrMhn7J6uC/wT8NQ\n" +
                    "HNUt1V6ikuTE932FLuX1XHXKuGpIqyQ2VmtOe1CSrsYCbzZGdT2eVecUcg+VDDpf\n" +
                    "T83WLkXyPbMVlQ0stPusT9oTP8GZEYBKQB6hkHFXYsKyd25TVx4=\n" +
                    "=M1G\n" +
                    "-----END PGP SIGNATURE-----\n";

    private static final String PUB_KEY =
                    "-----BEGIN PGP PUBLIC KEY BLOCK-----\n" +
                            "Comment: https://keybase.io/ashigarudev\n" +
                            "Version: Keybase Go 6.3.1 (linux)\n" +
                            "\n" +
                            "xsFNBGZdzx4BEADmL1E5gLoHtAd+N9Cw22VbnD47em9Hn946aDeB90pbrx02m8TW\n" +
                            "Acji5VOOmN1CNg2EomG0aGk6eox1TZkisYsu5rTCmpQX36CQ6/LvUFh8MTYF38kW\n" +
                            "wukNxE93wrXz/emk2yW/jeos6XlQ6/iJmom4bRCHDLxstFn14ICitr2zKysAOHkC\n" +
                            "iutQacwsGSLImi/7YEzQrIAi4WeTGrScyEFaJ0BxOQ4lzZeQw3Me+ESufZDOfB6+\n" +
                            "u8wsZzqVP5drp/AStbhGPhkYXbHJGikgVDVxxm/C9Yy/jhcQGUPSEFqXREeFncTM\n" +
                            "w7q3M5YG7Rl7m2VPEElNkZRYBI7fa5G5E6Iy01Y4/KxyutRwOf/DZHUaK/VQQQne\n" +
                            "HJzH58PvISPvswZzJWKN3mHiNGrbWGyBcvJOXlfbekLbRML8I28usKnSDWbHdkWc\n" +
                            "9Ls8P+H62TcY7npdGRvZAGIcM11BqGp66fndc911HDbX3/0IPp1DJEnpLn46gQqs\n" +
                            "3GJ6rMTBbt++krIFam1/kIr3Atp5EBqoSgAvxY5Xk+OUsYaa/K3VBQONpI2f7qJZ\n" +
                            "HN9GpqszwF2eeu1vKB/CRxISRQLjklVBssiZ2Zez7PZ470Ses1V7jK2tWGqzf5sG\n" +
                            "C0Tpp53WqFHtn4u/YuRtPQJtO0FHsc82mZbynoCO5YhNSh1mivPQoxPj0QARAQAB\n" +
                            "zQxBc2hpZ2FydSBEZXbCwXEEEwEKACUFAmZdzx4JEKE4BrH6KmdrAhsDBQsJCAcD\n" +
                            "BRUKCQgLBRYCAwEAAAD0txAAzpXmxtqVRLxEEdUBx1kxp1kE8kDJAhBraX5VXGOv\n" +
                            "HuThhcr3j5Esj4IOGcsiV5S9nRNPu+hjjTX8AoOVLQcfU0jymrNRBXLQcd7L03Jj\n" +
                            "0vG3sb7HOVbnQdGAwCrabb941BB3smitsYqI/Xz12CjavsONSp6wImt+jVHsAYC6\n" +
                            "y1xew4cBkPL9VmzKabTGNTV+wPe7xHSdptdAvK98EWFZ+Yq3ut/rt4mnqr35OQWW\n" +
                            "qDcAiAqKndqJXVZklDOvdQ654VPsBlJG4V+K4evZ7ECUc4gRVWWe5Ijl9z0UGopv\n" +
                            "FTkeTn9GnyHRZgLYooHkqd3oith/1fweldatvRGIXpdA1W02Tn7I0imjvzgBNDVq\n" +
                            "MS3rCp8kFFDtcshpASbtXChiloMFaw1+VDymT7sF81S5obbsJYRRkt2Qo+xM3B2n\n" +
                            "t0gZDMuLAJ2Er9VXxpcyrjl8U+Us8atbx7x4UyPaZJe4zj8nZYZly/uVZQ8JL/Nc\n" +
                            "zMg8ES9c8LV9ZcSlsIgX8VT6omxlSzWZNtfswBrXMUruxJgc7WKn1I6JMFbeRUG5\n" +
                            "fLtjLyn4/KufW+Liiq4RKcRQb/rxUaT+e7tzY90y4MqTzLD7kbVhCRx5RVBY5bZD\n" +
                            "2pFtch6CPVnZx/EHjR3Yd2zZgbDCVSIEEA6y2QS3aMhHXu1orgjVayOWVTINZE0y\n" +
                            "K3POwU0EZl3PHgEQAOOzDEJRk8paHDXqNGYiFiQZCxX3CIOK3+DR+zsS8oq4AtXT\n" +
                            "R7WUBDRACwUkDpNhybmkpEWH6B3zdsZPaGJ80ApTImWXc6KMJagcAJPVrwSGttOb\n" +
                            "zQHCsbsVfS3xXQ4G3uxncLd7Ck+fesR0GVsfJ4HsTOZaKmbuUYFifa4PevwEeYKR\n" +
                            "AcPdfcx7dTRd18XBaBPLNRzbUfck1rCIiO9QXR6oVbUYBlOKPVDYMjgrav4hd2s2\n" +
                            "BxWNLXxkE3MsyTSQ/+B8ty9Sz0C0aDrRRs5lA0/07hF9C3Wnv8op5XsUkO5eT7RD\n" +
                            "1PeWk+WiQURcQhAJsmrxjG7rXWQWaU8QR095Ldd1VRZXzPoLx8+iTNWqNRj/VuWw\n" +
                            "vhThYuWIP+RJTAV4kx/Mi8Os1dkV0KIKYQYsu+i0d7UBqL4LzCoY332Z/vJiaoVT\n" +
                            "+Aa4T7+/hgoG0VYF5ddSyDZv+CwUOzLO7fh/Tg4Jv1CpHKgwq4NELf6G7SVjrnKH\n" +
                            "LNd/JULHDMTpl6/RFn0rrwb/phmfQz0cbHU3ZXUJU5m9aqvjhdjV31+UP+Re0EBB\n" +
                            "JKDTHqzggTfPtpu8+nIRrfxm8pyHHxmt4pa4wUYujLnySLyPpMYLuAi3U7FUSHyo\n" +
                            "F3eZB1SeQ+9rQuZSRlvjXJTdNBDDUnJR9CiKC6K78jHKXHd5v7LPWh86g7SpABEB\n" +
                            "AAHCwXYEGAEKACAWIQREX4B5lvcFhrcVx7ihOAax+ipnawUCZl3PHgIbDAAKCRCh\n" +
                            "OAax+ipna9/OD/0bHstAeNKkUezn8QbI8ZuRXgkrcPo0EQ3dUNO6ZbyhqFUiM8Vt\n" +
                            "1syF2vX72+BNewwFsOAWHrDTRSZ09dO+M1c58I+Lr1AVP14jfYQ0mmPGY8ND9sk5\n" +
                            "WDheZjCbO6OJ55yQzC/ZTEra1Pxi3yWqcneyG3yX4z4ih3BazYIH3MR3EaSLVLjd\n" +
                            "eo3TqviWsBE7upKI1ipKf58l/0JoYWWWyVSVbEk/kjHlod19NjHzBvxzAX7I17Co\n" +
                            "+TMduAb2wrwVOqdDzOTS/X/KOAs7Q643rTgz9YqC2V/k9FLDKQIgqUvsADTnZtwF\n" +
                            "1fzL3U/xcJdh46Yy3lmyi2e9Rt6oVSGTaRiSWSlPYGAgiLYiHGTpLhpAmupNGdaj\n" +
                            "tJ0PZPoFehQ7zW75tOml1/8AIwUgzJsQHSKe3UCG7uSpXWT0sE4trfF71O0y0zoH\n" +
                            "hJZZq0X9O6iC3qLOGi8l4ZmhTJhBd3YlPqtugHuQWSiBABR2EoCxrhgbu0W5+Dp/\n" +
                            "db/0DMdwPhIwWwi1j6E3YKqQiz3q+mjUflUFiskJUeaYQe+YaeXJ43bZ4WPXZcfy\n" +
                            "5WEKWZypGiuhirhfSrdmt4EPWQ3fR2j7/RafEpMsF9cWDvAoAvQQK3VM/EoCcj12\n" +
                            "qbgNKNuFv/4hw+BF2AUIM3SojZ6yqaNw2NByy3zKd5Wx1U4Pd6OY4Jcrxg==\n" +
                            "=iJA5\n" +
                            "-----END PGP PUBLIC KEY BLOCK-----\n";

    @Test
    public void should_verify_message() {
        Assert.assertTrue(verifySignedMessage(
                SIGNED_MESSAGE,
                PUB_KEY));
    }

    @Test
    public void should_no_verify_message() {
        Assert.assertFalse(verifySignedMessage(
                BAD_SIGNED_MESSAGE,
                PUB_KEY));
    }

    @Test
    public void should_verify_all_of_0013_messages() {
        final ClassLoader classLoader = VerifyPGPSignedClearMessageUtilTest.class.getClassLoader();
        final DecimalFormat decimalFormat = new DecimalFormat("00");
        for (int i = 1; i <= 12; ++i) {
            final String format = decimalFormat.format(i);
            final String filePath = format("0013_signed_message/0013-%s/signedmessage.txt", format);
            final InputStream inputStream = classLoader.getResourceAsStream(filePath);
            if (inputStream == null) {
                throw new IllegalArgumentException(format("File %s not found !", filePath));
            }
            final String signedMessage = new BufferedReader(new InputStreamReader(inputStream))
                    .lines()
                    .collect(Collectors.joining("\n"));
            Assert.assertTrue(
                    filePath,
                    verifySignedMessage(signedMessage, PUB_KEY));
        }
    }

}
