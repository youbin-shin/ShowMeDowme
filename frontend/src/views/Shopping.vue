<template>
  <div class="shopping">
    <div v-if="member">
      <v-icon @click="$router.push({ path: '/perparation' })">
        mdi-arrow-left
      </v-icon>
    </div>
    <div v-else>
      <v-icon @click="$router.push({ path: '/nonMember/perparation' })">
        mdi-arrow-left
      </v-icon>
    </div>
    <h1>장보는 중</h1>

    <v-row>
      <v-col cols="2">
        <ShoppingMemo />
      </v-col>
      <v-col v-if="aimTime">
        <v-row>
          <v-col>
            <h5>남은시간</h5>
          </v-col>
          <v-col>
            <section id="app">
              <div class="grid-container">
                <div class="grid-x">
                  <div class="cell flex flex-column">
                    <div id="timer">
                      <span id="minutes">{{ hoursLeft }}</span
                      ><span id="middle">:</span
                      ><span id="seconds">{{ minutesLeft }}</span
                      >:<span id="seconds">{{ secondsLeft }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </v-col>
        </v-row>
        <v-progress-linear
          :color="timerColor"
          height="10"
          :value="timer"
          striped
        ></v-progress-linear>
      </v-col>
    </v-row>
    <div v-if="recentItem.length">
      <h4>최근 사진으로 추가된 제품</h4>
      <div>제품명 : {{ recentItem.name }}</div>
      <div>가격 : {{ recentItem.price }}</div>
    </div>

    <v-btn
      class="camera-btn"
      dark
      rounded
      large
      color="teal lighten-2"
      @click="$router.push({ path: '/camera' })"
    >
      <v-icon>mdi-camera </v-icon>

      사진으로 제품 등록
    </v-btn>
    <small class="camera-btn">사진으로 간편하게 제품을 등록하세요.</small>
    <ShoppingList />

    <v-row class="mt-3 final-box">
      <v-col>
        <h4>현재 결제 예상 금액 {{ nowExpense }}원</h4>
      </v-col>
      <v-col>
        <v-btn outlined @click="completeShop()"> 장보기 완료 </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import "@/assets/css/views/shopping.scss";
import ShoppingList from "@/components/Shopping/ShoppingList";
import ShoppingMemo from "@/components/Shopping/ShoppingMemo";
import axios from "axios";
import SERVER from "@/api/spring";
import { mapState, mapActions } from "vuex";

export default {
  name: "Shopping",
  components: {
    ShoppingMemo,
    ShoppingList,
  },
  props: {
    endpoint: {},
  },
  created() {
    if (sessionStorage.length === 0) {
      this.member = false;
    } else {
      this.username = sessionStorage.userid;
    }
    this.hoursLeft = parseInt(this.aimTime / 60);
    this.minutesLeft = this.aimTime % 60;
  },
  mounted() {
    this.$nextTick(function () {
      window.setInterval(() => {
        this.timer = parseInt(
          ((this.aimTime - this.hoursLeft * 60 - this.minutesLeft) /
            this.aimTime) *
            100
        );
        if (this.hoursLeft === 0 && this.minutesLeft === 10) {
          this.timerColor = "red lighten-1";
        }
        if (this.secondsLeft > 0) {
          this.secondsLeft--;
        } else if (this.secondsLeft == 0 && this.minutesLeft > 0) {
          this.secondsLeft = 59;
          this.minutesLeft--;
        } else if (
          this.secondsLeft == 0 &&
          this.minutesLeft == 0 &&
          this.hoursLeft > 0
        ) {
          this.secondsLeft = 59;
          this.minutesLeft = 59;
          this.hoursLeft--;
        } else if (
          this.secondsLeft == 0 &&
          this.minutesLeft == 0 &&
          this.hoursLeft == 0
        ) {
          if (this.aimTime !== 0) {
            alert("쇼핑시간이 초과하였습니다");
            this.failTime();
            this.secondsLeft--;
          }
        }
      }, 1000);
    });
  },
  computed: {
    ...mapState([
      "isSkipTime",
      "isSkipMoney",
      "aimTime",
      "aimExpense",
      "nowExpense",
      "recentItem",
      "shoppingList",
      "check",
    ]),
    timeLeft: function () {
      if (this.hours !== 0) {
        return (
          this.hoursLeft +
          ":" +
          this.zeroPad(this.minutesLeft, 2) +
          ":" +
          this.zeroPad(this.secondsLeft, 2)
        );
      } else if (this.minutes !== 0) {
        return this.minutesLeft + ":" + this.zeroPad(this.secondsLeft, 2);
      } else {
        return this.secondsLeft;
      }
    },
  },
  methods: {
    ...mapActions(["saveGrade"]),
    completeShop() {
      const URL = SERVER.URL + SERVER.ROUTES.getCalendar;
      let stirngShoppingList = "";
      for (let i = 0; i < this.shoppingList.length; i++) {
        stirngShoppingList +=
          this.shoppingList[i].name +
          "," +
          this.shoppingList[i].amount +
          "," +
          (this.shoppingList[i].amount * this.shoppingList[i].price) +
          ",";
      }
      if (stirngShoppingList !== "") {
        stirngShoppingList = stirngShoppingList.substr(
          0,
          stirngShoppingList.length - 1
        );
      }
      // console.log(stirngShoppingList);
      let sendData = {
        userId: this.username,
        money: this.nowExpense,
        moneycheck: this.check.moneycheck,
        timecheck: this.check.timecheck,
        shoppinglist: stirngShoppingList,
      };
      axios
        .post(URL, sendData)
        .then((res) => {
          this.saveGrade(res.data.grade);
          this.$router.push({ path: "/report" });
        })
        .catch((err) => {
          console.err(err);
        });
    },
    zeroPad(input, length) {
      return (Array(length + 1).join("0") + input).slice(-length);
    },
  },
  data() {
    return {
      hoursLeft: 0,
      minutesLeft: 0,
      secondsLeft: 0,
      timer: 0,
      timerColor: "teal lighten-2",
      member: true,
      username: "",
    };
  },
};
</script>

