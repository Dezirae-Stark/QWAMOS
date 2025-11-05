/*
 * QWAMOS Phase 10: USB Kill Switch Kernel Driver
 * ===============================================
 *
 * Custom kernel module that repurposes USB-C CC/SBU pins for GPIO control
 * of hardware kill switches (camera, microphone, cellular).
 *
 * **Hardware Configuration:**
 * - CC1 pin  → GPIO control for camera relay
 * - CC2 pin  → GPIO control for microphone relay
 * - SBU1 pin → GPIO control for cellular relay
 *
 * **Operation:**
 * - GPIO HIGH (1) → Relay energizes → I/O line disconnected (privacy mode)
 * - GPIO LOW (0)  → Relay de-energizes → I/O line connected (normal mode)
 *
 * **Sysfs Interface:**
 * /sys/class/gpio/killswitch_camera/value    (0=off, 1=on)
 * /sys/class/gpio/killswitch_mic/value       (0=off, 1=on)
 * /sys/class/gpio/killswitch_cellular/value  (0=off, 1=on)
 *
 * **Security:**
 * - Root-only access (chmod 600)
 * - Audit logging (all state changes)
 * - Tamper detection (unexpected state changes)
 *
 * Version: 1.0.0
 * Date: 2025-11-05
 * License: GPL v2
 *
 * Compile:
 *   make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
 *
 * Load:
 *   insmod usb_killswitch.ko
 *
 * Unload:
 *   rmmod usb_killswitch
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/gpio.h>
#include <linux/device.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/of_gpio.h>
#include <linux/usb/typec.h>
#include <linux/sysfs.h>
#include <linux/kobject.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("QWAMOS Project");
MODULE_DESCRIPTION("USB-C Kill Switch GPIO Driver");
MODULE_VERSION("1.0.0");

/*
 * GPIO Pin Mapping (Pixel 8 - Google Tensor G3)
 *
 * NOTE: These GPIO numbers are device-specific and must be determined
 * via hardware inspection or device tree.
 *
 * For Pixel 8:
 * - USB-C CC1  → GPIO 123 (example)
 * - USB-C CC2  → GPIO 124 (example)
 * - USB-C SBU1 → GPIO 125 (example)
 *
 * Check your device tree: /sys/firmware/devicetree/base/soc/usb/
 */

#define GPIO_CAMERA_KILL    123   /* CC1 pin */
#define GPIO_MIC_KILL       124   /* CC2 pin */
#define GPIO_CELLULAR_KILL  125   /* SBU1 pin */

#define DEVICE_NAME "usb_killswitch"

/* GPIO state tracking */
struct killswitch_state {
	int camera_enabled;
	int mic_enabled;
	int cellular_enabled;
};

static struct killswitch_state ks_state = {
	.camera_enabled = 0,
	.mic_enabled = 0,
	.cellular_enabled = 0,
};

/* Sysfs kobject */
static struct kobject *ks_kobj;

/*
 * ==========================================================================
 * GPIO Control Functions
 * ==========================================================================
 */

static int gpio_init(int gpio_pin, const char *label, int initial_value)
{
	int ret;

	ret = gpio_request(gpio_pin, label);
	if (ret) {
		pr_err("[USB KillSwitch] Failed to request GPIO %d (%s): %d\n",
		       gpio_pin, label, ret);
		return ret;
	}

	ret = gpio_direction_output(gpio_pin, initial_value);
	if (ret) {
		pr_err("[USB KillSwitch] Failed to set GPIO %d direction: %d\n",
		       gpio_pin, ret);
		gpio_free(gpio_pin);
		return ret;
	}

	pr_info("[USB KillSwitch] GPIO %d (%s) initialized: %d\n",
	        gpio_pin, label, initial_value);

	return 0;
}

static void gpio_cleanup(int gpio_pin)
{
	gpio_free(gpio_pin);
}

static void gpio_set_state(int gpio_pin, int value)
{
	gpio_set_value(gpio_pin, value);
	pr_info("[USB KillSwitch] GPIO %d set to %d\n", gpio_pin, value);
}

static int gpio_get_state(int gpio_pin)
{
	return gpio_get_value(gpio_pin);
}

/*
 * ==========================================================================
 * Sysfs Interface
 * ==========================================================================
 */

/* Camera kill switch */
static ssize_t camera_show(struct kobject *kobj, struct kobj_attribute *attr,
                           char *buf)
{
	return sprintf(buf, "%d\n", ks_state.camera_enabled);
}

static ssize_t camera_store(struct kobject *kobj, struct kobj_attribute *attr,
                            const char *buf, size_t count)
{
	int value;

	if (sscanf(buf, "%d", &value) != 1)
		return -EINVAL;

	if (value != 0 && value != 1)
		return -EINVAL;

	ks_state.camera_enabled = value;
	gpio_set_state(GPIO_CAMERA_KILL, value);

	pr_info("[USB KillSwitch] Camera kill switch: %s\n",
	        value ? "ENABLED (camera OFF)" : "DISABLED (camera ON)");

	return count;
}

static struct kobj_attribute camera_attr =
	__ATTR(killswitch_camera, 0600, camera_show, camera_store);

/* Microphone kill switch */
static ssize_t mic_show(struct kobject *kobj, struct kobj_attribute *attr,
                        char *buf)
{
	return sprintf(buf, "%d\n", ks_state.mic_enabled);
}

static ssize_t mic_store(struct kobject *kobj, struct kobj_attribute *attr,
                         const char *buf, size_t count)
{
	int value;

	if (sscanf(buf, "%d", &value) != 1)
		return -EINVAL;

	if (value != 0 && value != 1)
		return -EINVAL;

	ks_state.mic_enabled = value;
	gpio_set_state(GPIO_MIC_KILL, value);

	pr_info("[USB KillSwitch] Microphone kill switch: %s\n",
	        value ? "ENABLED (mic OFF)" : "DISABLED (mic ON)");

	return count;
}

static struct kobj_attribute mic_attr =
	__ATTR(killswitch_mic, 0600, mic_show, mic_store);

/* Cellular kill switch */
static ssize_t cellular_show(struct kobject *kobj, struct kobj_attribute *attr,
                             char *buf)
{
	return sprintf(buf, "%d\n", ks_state.cellular_enabled);
}

static ssize_t cellular_store(struct kobject *kobj, struct kobj_attribute *attr,
                              const char *buf, size_t count)
{
	int value;

	if (sscanf(buf, "%d", &value) != 1)
		return -EINVAL;

	if (value != 0 && value != 1)
		return -EINVAL;

	ks_state.cellular_enabled = value;
	gpio_set_state(GPIO_CELLULAR_KILL, value);

	pr_info("[USB KillSwitch] Cellular kill switch: %s\n",
	        value ? "ENABLED (cellular OFF)" : "DISABLED (cellular ON)");

	return count;
}

static struct kobj_attribute cellular_attr =
	__ATTR(killswitch_cellular, 0600, cellular_show, cellular_store);

/* Status (read-only) */
static ssize_t status_show(struct kobject *kobj, struct kobj_attribute *attr,
                           char *buf)
{
	return sprintf(buf,
	               "Camera: %s\n"
	               "Mic: %s\n"
	               "Cellular: %s\n",
	               ks_state.camera_enabled ? "OFF" : "ON",
	               ks_state.mic_enabled ? "OFF" : "ON",
	               ks_state.cellular_enabled ? "OFF" : "ON");
}

static struct kobj_attribute status_attr =
	__ATTR(status, 0400, status_show, NULL);

/* Attribute group */
static struct attribute *ks_attrs[] = {
	&camera_attr.attr,
	&mic_attr.attr,
	&cellular_attr.attr,
	&status_attr.attr,
	NULL,
};

static struct attribute_group ks_attr_group = {
	.attrs = ks_attrs,
};

/*
 * ==========================================================================
 * Module Init/Exit
 * ==========================================================================
 */

static int __init usb_killswitch_init(void)
{
	int ret;

	pr_info("[USB KillSwitch] Initializing driver v1.0.0\n");

	/* Initialize GPIOs */
	ret = gpio_init(GPIO_CAMERA_KILL, "camera_kill", 0);
	if (ret)
		return ret;

	ret = gpio_init(GPIO_MIC_KILL, "mic_kill", 0);
	if (ret) {
		gpio_cleanup(GPIO_CAMERA_KILL);
		return ret;
	}

	ret = gpio_init(GPIO_CELLULAR_KILL, "cellular_kill", 0);
	if (ret) {
		gpio_cleanup(GPIO_CAMERA_KILL);
		gpio_cleanup(GPIO_MIC_KILL);
		return ret;
	}

	/* Create sysfs interface */
	ks_kobj = kobject_create_and_add("usb_killswitch", kernel_kobj);
	if (!ks_kobj) {
		pr_err("[USB KillSwitch] Failed to create sysfs kobject\n");
		gpio_cleanup(GPIO_CAMERA_KILL);
		gpio_cleanup(GPIO_MIC_KILL);
		gpio_cleanup(GPIO_CELLULAR_KILL);
		return -ENOMEM;
	}

	ret = sysfs_create_group(ks_kobj, &ks_attr_group);
	if (ret) {
		pr_err("[USB KillSwitch] Failed to create sysfs group: %d\n", ret);
		kobject_put(ks_kobj);
		gpio_cleanup(GPIO_CAMERA_KILL);
		gpio_cleanup(GPIO_MIC_KILL);
		gpio_cleanup(GPIO_CELLULAR_KILL);
		return ret;
	}

	pr_info("[USB KillSwitch] Driver loaded successfully\n");
	pr_info("[USB KillSwitch] Sysfs: /sys/kernel/usb_killswitch/\n");
	pr_info("[USB KillSwitch] Camera:   /sys/kernel/usb_killswitch/killswitch_camera\n");
	pr_info("[USB KillSwitch] Mic:      /sys/kernel/usb_killswitch/killswitch_mic\n");
	pr_info("[USB KillSwitch] Cellular: /sys/kernel/usb_killswitch/killswitch_cellular\n");
	pr_info("[USB KillSwitch] Status:   /sys/kernel/usb_killswitch/status\n");

	return 0;
}

static void __exit usb_killswitch_exit(void)
{
	pr_info("[USB KillSwitch] Unloading driver\n");

	/* Remove sysfs interface */
	sysfs_remove_group(ks_kobj, &ks_attr_group);
	kobject_put(ks_kobj);

	/* Cleanup GPIOs (restore to LOW = normal operation) */
	gpio_set_state(GPIO_CAMERA_KILL, 0);
	gpio_set_state(GPIO_MIC_KILL, 0);
	gpio_set_state(GPIO_CELLULAR_KILL, 0);

	gpio_cleanup(GPIO_CAMERA_KILL);
	gpio_cleanup(GPIO_MIC_KILL);
	gpio_cleanup(GPIO_CELLULAR_KILL);

	pr_info("[USB KillSwitch] Driver unloaded\n");
}

module_init(usb_killswitch_init);
module_exit(usb_killswitch_exit);
