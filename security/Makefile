.PHONY: help dev-emu deploy test clean install-deps

help:
	@echo "QWAMOS Security Layer - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  install-deps  - Install dependencies (Termux/Debian)"
	@echo "  dev-emu       - Start development emulator (Linux laptop)"
	@echo "  deploy        - Deploy to Motorola Edge 2025"
	@echo "  test          - Run test suite"
	@echo "  clean         - Stop all services and clean temp files"
	@echo ""

install-deps:
	@echo "Installing QWAMOS dependencies..."
	@echo ""
	@echo "[1/4] System packages..."
	pkg install -y python tor iptables git signify || \
	apt-get install -y python3 python3-pip tor iptables git signify-openbsd

	@echo ""
	@echo "[2/4] Python packages..."
	pip3 install watchdog pycryptodome

	@echo ""
	@echo "[3/4] Creating directories..."
	mkdir -p /etc/qwamos/keys
	mkdir -p /var/run/qwamos/control-bus
	mkdir -p /data/qwamos/{firewall,radio,session-keys}

	@echo ""
	@echo "[4/4] Generating Dom0 signing keys..."
	if [ ! -f /etc/qwamos/keys/dom0.sec ]; then \
		cd /etc/qwamos/keys && signify -G -p dom0.pub -s dom0.sec; \
		echo "✅ Keys generated"; \
	else \
		echo "ℹ️  Keys already exist"; \
	fi

	@echo ""
	@echo "✅ Dependencies installed"

dev-emu:
	@echo "Starting QWAMOS development emulator..."
	@echo ""
	@echo "This simulates the 4-VM architecture on your laptop"
	@echo ""

	@echo "[1/4] Starting Dom0 policy daemon..."
	python3 dom0/qwamosd/qwamosd.py &
	@sleep 2

	@echo "[2/4] Starting Gateway VM policy listener..."
	python3 gateway_vm/policy/gateway-policyd.py &
	@sleep 1

	@echo "[3/4] Applying initial policy..."
	cp dom0/policy/policy.conf.example /etc/qwamos/policy.conf

	@echo "[4/4] Starting radio monitor..."
	bash gateway_vm/radio/radio-ctrl.sh monitor &

	@echo ""
	@echo "✅ Dev emulator running"
	@echo ""
	@echo "Test commands:"
	@echo "  - View policy: cat /etc/qwamos/policy.conf"
	@echo "  - Change setting: edit /etc/qwamos/policy.conf"
	@echo "  - Radio status: bash gateway_vm/radio/radio-ctrl.sh status"
	@echo "  - Stop: make clean"
	@echo ""

deploy:
	@echo "QWAMOS Security Layer - Device Deployment"
	@echo "=========================================="
	@echo ""
	./deploy-to-device.sh

test:
	@echo "Running QWAMOS test suite..."
	@echo ""

	@echo "[1/5] Testing policy schema validation..."
	python3 -c "import json; json.load(open('dom0/policy/policy.schema.json'))"
	@echo "✅ Schema valid"

	@echo ""
	@echo "[2/5] Testing policy parsing..."
	python3 -c "exec(open('dom0/qwamosd/qwamosd.py').read().split('class PolicyDaemon')[0]); \
	            d = PolicyDaemon(); d.load_current_policy()"
	@echo "✅ Policy parsing OK"

	@echo ""
	@echo "[3/5] Testing firewall rules syntax..."
	bash -n gateway_vm/firewall/rules-basic.sh
	bash -n gateway_vm/firewall/rules-strict.sh
	@echo "✅ Firewall scripts valid"

	@echo ""
	@echo "[4/5] Testing radio controller..."
	bash -n gateway_vm/radio/radio-ctrl.sh
	@echo "✅ Radio controller valid"

	@echo ""
	@echo "[5/5] Testing Gateway policy daemon..."
	python3 -c "exec(open('gateway_vm/policy/gateway-policyd.py').read())"
	@echo "✅ Gateway daemon valid"

	@echo ""
	@echo "✅ All tests passed"

clean:
	@echo "Stopping QWAMOS services..."
	pkill -f qwamosd || true
	pkill -f gateway-policyd || true
	pkill -f radio-ctrl || true
	@echo "✅ Services stopped"

	@echo "Cleaning temp files..."
	rm -f /var/run/qwamos/radio-state
	rm -f /var/run/qwamos/radio-last-rx
	@echo "✅ Cleanup complete"
