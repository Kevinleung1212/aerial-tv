package app.orchard.tv.apps

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/** Identification must only follow meaningful HDMI-CEC names, never infer from a port number. */
class SourceDeviceDetectionTest {
    @Test fun detectsKnownCecDevices() {
        assertEquals(SourceDevice.AppleTv, SourceDevice.fromCecName("Living Room Apple TV"))
        assertEquals(SourceDevice.PlayStation, SourceDevice.fromCecName("PLAYSTATION 5"))
        assertEquals(SourceDevice.PlayStation, SourceDevice.fromCecName("PS5"))
        assertEquals(SourceDevice.Switch, SourceDevice.fromCecName("Nintendo Switch"))
        assertEquals(SourceDevice.Xbox, SourceDevice.fromCecName("Xbox Series X"))
        assertEquals(SourceDevice.Computer, SourceDevice.fromCecName("Mac mini"))
        assertEquals(SourceDevice.SetTopBox, SourceDevice.fromCecName("IPTV Box"))
    }

    @Test fun doesNotGuessFromGenericSourceNames() {
        assertNull(SourceDevice.fromCecName(null))
        assertNull(SourceDevice.fromCecName(""))
        assertNull(SourceDevice.fromCecName("HDMI 1"))
        assertNull(SourceDevice.fromCecName("Playback 1"))
        assertNull(SourceDevice.fromCecName("Unknown"))
    }
}
